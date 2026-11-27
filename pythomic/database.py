"""Camada de banco de dados (SQLite) do Pythomic.

Schema:
    users(id, name_hash UNIQUE, name_enc, email_hash UNIQUE, email_enc,
          password, profile_pic, created_at)
    pending_regs(id, email_hash UNIQUE, name_hash, name_enc, email_enc,
                 password, code, created_at)  -- cadastro aguardando código
    posts(id, user_id FK, text_enc, media, created_at)
    followers(follower_id, following_id, PK)
    likes(user_id, post_id, PK)
    post_views(post_id FK, user_id FK, viewed_at, PK)

Todas as consultas usam parâmetros (?) — nunca formatação de strings — para
eliminar risco de SQL Injection. Os campos protegidos (text_enc, name_enc,
email_enc) só são descriptografados na memória do servidor, já no formato
pronto para a interface.
"""

import time
from contextlib import contextmanager

from .config import DB_NAME, DEFAULT_AVATAR
from .security import (
    decrypt_field,
    encrypt_field,
    hash_password,
    lookup_hash,
    verify_password,
)


@contextmanager
def _conn():
    """Conexão SQLite endurecida: WAL, foreign_keys e busy_timeout."""
    import sqlite3

    conn = sqlite3.connect(DB_NAME, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Cria o schema (idempotente) e os índices usados pelo feed."""
    with _conn() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_hash TEXT UNIQUE NOT NULL,
                name_enc TEXT,
                email_hash TEXT UNIQUE NOT NULL,
                email_enc TEXT,
                password TEXT NOT NULL,
                profile_pic TEXT,
                created_at INTEGER NOT NULL)"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS pending_regs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_hash TEXT UNIQUE NOT NULL,
                name_hash TEXT NOT NULL,
                name_enc TEXT,
                email_enc TEXT,
                password TEXT NOT NULL,
                code TEXT NOT NULL,
                created_at INTEGER NOT NULL)"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text_enc TEXT,
                media TEXT,
                created_at INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS followers (
                follower_id INTEGER NOT NULL,
                following_id INTEGER NOT NULL,
                PRIMARY KEY (follower_id, following_id))"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS likes (
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, post_id))"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS post_views (
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                viewed_at INTEGER NOT NULL,
                PRIMARY KEY (post_id, user_id),
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_posts_user ON posts(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_likes_post ON likes(post_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_followers_target ON followers(following_id)")


def safe_user(row):
    """Converte a linha do usuário em um dicionário SEGURO para a interface.

    Devolvemos somente o que a UI precisa exibir — o hash da senha e as
    colunas internas NUNCA saem do servidor.
    """
    if row is None:
        return None
    return {
        "id": row["id"],
        "name": decrypt_field(row["name_enc"]) or "Usuário",
        "email": decrypt_field(row["email_enc"]),
        "profile_pic": row["profile_pic"] or DEFAULT_AVATAR,
        "created": row["created_at"],
    }


def register_user(name, email, password):
    """Cadastra um usuário. Retorna o novo id ou None (inválido/duplicado).

    A unicidade é garantida pelas colunas name_hash/email_hash (HMAC-SHA256),
    nunca pelo texto puro — que nem chega a ficar armazenado sem criptografia.
    """
    import sqlite3

    name = (name or "").strip()
    email = (email or "").strip().lower()
    if not name or not email or not password:
        return None
    from .security import password_policy_error
    if password_policy_error(password):  # defesa extra: a UI também valida
        return None
    try:
        with _conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (name_hash, name_enc, email_hash, email_enc,"
                " password, profile_pic, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    lookup_hash(name.lower()),
                    encrypt_field(name),
                    lookup_hash(email),
                    encrypt_field(email),
                    hash_password(password),
                    DEFAULT_AVATAR,
                    int(time.time()),
                ),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        # Violação de UNIQUE em name_hash/email_hash: já cadastrado.
        return None


def login_user(name, password):
    """Autentica buscando por name_hash (login por nome de usuário, não email).

    O nome é normalizado (strip + lower) para login case-insensitive, como já
    acontecia com o email. Retorna a linha completa ou None. ATENÇÃO: a linha
    inclui o hash da senha — use sempre safe_user() antes de enviar qualquer
    dado de usuário para a interface.
    """
    nome = (name or "").strip().lower()
    if not nome:
        return None
    name_hash = lookup_hash(nome)
    with _conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE name_hash = ?", (name_hash,)).fetchone()
    if row and verify_password(password or "", row["password"]):
        return row
    return None


def get_user_by_id(user_id):
    with _conn() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def update_password(user_id, new_password):
    with _conn() as conn:
        conn.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hash_password(new_password), user_id),
        )


def create_pending_registration(name, email, password):
    """Cria um cadastro PENDENTE (aguardando o código de verificação por email).

    Guarda name/email criptografados, a senha já hasheada e o código de
    verificação. Retorna o código (para o chamador enviar por email) ou None
    se o nome/email já estiver em uso por uma conta ativa. Se já existe um
    pendente para o email, renova os dados e o código (reenvio).
    """
    import sqlite3

    from .mailer import generate_code

    name = (name or "").strip()
    email = (email or "").strip().lower()
    if not name or not email or not password:
        return None
    from .security import password_policy_error
    if password_policy_error(password):  # defesa extra: a UI também valida
        return None
    name_hash = lookup_hash(name.lower())
    email_hash = lookup_hash(email)
    code = generate_code()
    agora = int(time.time())
    with _conn() as conn:
        # Nome/email já em uso por conta ativa? (não pode haver dois)
        if conn.execute("SELECT 1 FROM users WHERE name_hash = ?", (name_hash,)).fetchone():
            return None
        if conn.execute("SELECT 1 FROM users WHERE email_hash = ?", (email_hash,)).fetchone():
            return None
        try:
            conn.execute(
                "INSERT INTO pending_regs (email_hash, name_hash, name_enc, email_enc,"
                " password, code, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (email_hash, name_hash, encrypt_field(name), encrypt_field(email),
                 hash_password(password), code, agora),
            )
        except sqlite3.IntegrityError:
            # Já existe pendente para o email: renova dados + código (reenvio).
            conn.execute(
                "UPDATE pending_regs SET name_hash=?, name_enc=?, email_enc=?,"
                " password=?, code=?, created_at=? WHERE email_hash=?",
                (name_hash, encrypt_field(name), encrypt_field(email),
                 hash_password(password), code, agora, email_hash),
            )
    return code


def verify_pending_registration(email, code):
    """Confirma o código e cria a conta ativa. Retorna o novo id ou None.

    None se: não há pendente para o email, código errado, código expirado ou
    nome/email foi tomado por outra conta entre o cadastro pendente e a
    confirmação (corrida rara).
    """
    import sqlite3

    from .config import VERIFY_CODE_EXPIRY

    email_hash = lookup_hash((email or "").strip().lower())
    code = (code or "").strip()
    if not code:
        return None
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM pending_regs WHERE email_hash = ?", (email_hash,)
        ).fetchone()
        if row is None:
            return None
        # Código expirado? Remove o pendente (vencido não serve mais).
        if int(time.time()) - row["created_at"] > VERIFY_CODE_EXPIRY:
            conn.execute("DELETE FROM pending_regs WHERE id = ?", (row["id"],))
            return None
        if row["code"] != code:
            return None
        try:
            cur = conn.execute(
                "INSERT INTO users (name_hash, name_enc, email_hash, email_enc,"
                " password, profile_pic, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (row["name_hash"], row["name_enc"], row["email_hash"],
                 row["email_enc"], row["password"], DEFAULT_AVATAR, int(time.time())),
            )
            uid = cur.lastrowid
            conn.execute("DELETE FROM pending_regs WHERE id = ?", (row["id"],))
            return uid
        except sqlite3.IntegrityError:
            # Nome/email tomado entre o pendente e a confirmação.
            return None


def resend_verification_code(email):
    """Gera um novo código para o pendente existente. Retorna o código ou None."""
    from .mailer import generate_code

    email_hash = lookup_hash((email or "").strip().lower())
    code = generate_code()
    agora = int(time.time())
    with _conn() as conn:
        cur = conn.execute(
            "UPDATE pending_regs SET code=?, created_at=? WHERE email_hash=?",
            (code, agora, email_hash),
        )
        if cur.rowcount == 0:
            return None
    return code


def recover_password(email):
    """Recuperação de senha: gera nova senha aleatória e substitui no banco.

    Retorna (True, nova_senha) se a conta existir, ou (False, None) caso
    contrário. O chamador envia a nova senha por email (mailer.send_new_password).
    """
    from .mailer import generate_password

    email_hash = lookup_hash((email or "").strip().lower())
    with _conn() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE email_hash = ?", (email_hash,)
        ).fetchone()
        if row is None:
            return False, None
        nova = generate_password()
        conn.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hash_password(nova), row["id"]),
        )
    return True, nova


def delete_user(user_id):
    """Exclui a conta e TODOS os dados relacionados.

    Devolve a lista de caminhos de mídia (posts + avatar) para o chamador
    apagar do disco (uploads.delete_media). A exclusão do usuário cai em
    CASCADE para posts e post_views; likes e followers não têm FK e são
    apagados explicitamente.
    """
    with _conn() as conn:
        # Mídia dos posts + avatar ANTES de excluir (cascade apaga posts).
        midias = [
            r["media"]
            for r in conn.execute(
                "SELECT media FROM posts WHERE user_id = ?", (user_id,)
            ).fetchall()
            if r["media"]
        ]
        avatar = conn.execute(
            "SELECT profile_pic FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if avatar and avatar["profile_pic"]:
            midias.append(avatar["profile_pic"])
        # likes/followers sem FK: apagam à mão (likes dados E recebidos;
        # seguidores E seguindo).
        conn.execute("DELETE FROM likes WHERE user_id = ?", (user_id,))
        conn.execute(
            "DELETE FROM likes WHERE post_id IN (SELECT id FROM posts WHERE user_id = ?)",
            (user_id,),
        )
        conn.execute("DELETE FROM followers WHERE follower_id = ?", (user_id,))
        conn.execute("DELETE FROM followers WHERE following_id = ?", (user_id,))
        conn.execute("DELETE FROM post_views WHERE user_id = ?", (user_id,))
        # posts + post_views caem por CASCADE ao apagar o usuário.
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    return midias


def get_user_stats(user_id):
    """Estatísticas do usuário: seguidores, seguindo, posts e views acumuladas.

    As views somam TODAS as visualizações únicas recebidas pelos posts do
    usuário (uma por usuário por post — veja a tabela post_views).
    """
    with _conn() as conn:
        seguidores = conn.execute(
            "SELECT COUNT(*) AS total FROM followers WHERE following_id = ?", (user_id,)
        ).fetchone()["total"]
        seguindo = conn.execute(
            "SELECT COUNT(*) AS total FROM followers WHERE follower_id = ?", (user_id,)
        ).fetchone()["total"]
        posts = conn.execute(
            "SELECT COUNT(*) AS total FROM posts WHERE user_id = ?", (user_id,)
        ).fetchone()["total"]
        views = conn.execute(
            "SELECT COUNT(*) AS total FROM post_views v JOIN posts p ON p.id = v.post_id"
            " WHERE p.user_id = ?",
            (user_id,),
        ).fetchone()["total"]
    return {"followers": seguidores, "following": seguindo, "posts": posts, "views": views}


def is_following(follower_id, following_id) -> bool:
    """Verifica se follower_id já segue following_id (consulta indexada)."""
    with _conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM followers WHERE follower_id = ? AND following_id = ?",
            (follower_id, following_id),
        ).fetchone()
    return row is not None


def update_profile_pic(user_id, pic_path) -> None:
    """Grava o novo caminho da foto de perfil (arquivo servido por /uploads)."""
    with _conn() as conn:
        conn.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (pic_path, user_id))


def toggle_follow(follower_id, following_id):
    """Segue/deixa de seguir. Retorna True se passou a seguir, False se parou."""
    with _conn() as conn:
        cur = conn.execute(
            "DELETE FROM followers WHERE follower_id = ? AND following_id = ?",
            (follower_id, following_id),
        )
        if cur.rowcount:
            return False
        conn.execute(
            "INSERT OR IGNORE INTO followers (follower_id, following_id) VALUES (?, ?)",
            (follower_id, following_id),
        )
        return True


def create_post(user_id, text, media_path=None):
    """Cria um post: texto criptografado (text_enc) + timestamp de criação."""
    with _conn() as conn:
        conn.execute(
            "INSERT INTO posts (user_id, text_enc, media, created_at) VALUES (?, ?, ?, ?)",
            (user_id, encrypt_field((text or "").strip()), media_path, int(time.time())),
        )


def toggle_like(user_id, post_id):
    """Curti/descurti. Retorna True se passou a curtir, False se parou."""
    with _conn() as conn:
        cur = conn.execute(
            "DELETE FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id)
        )
        if cur.rowcount:
            return False
        conn.execute(
            "INSERT OR IGNORE INTO likes (user_id, post_id) VALUES (?, ?)", (user_id, post_id)
        )
        return True


def delete_post(user_id, post_id):
    """Exclui um post do próprio usuário e devolve o caminho da mídia.

    Só remove se o post pertencer ao user_id — assim um usuário nunca exclui
    posts de outros (defesa em profundidade além da checagem da interface). As
    curtidas são apagadas explicitamente porque a tabela `likes` não tem FK com
    CASCADE; as `post_views` caem sozinhas pelo ON DELETE CASCADE do próprio
    post. Retorna o caminho da mídia (para o chamador apagar do disco) ou None
    se o post não existir/não for do usuário.
    """
    with _conn() as conn:
        row = conn.execute(
            "SELECT media FROM posts WHERE id = ? AND user_id = ?", (post_id, user_id)
        ).fetchone()
        if row is None:
            return None
        media = row["media"]
        conn.execute("DELETE FROM likes WHERE post_id = ?", (post_id,))
        conn.execute("DELETE FROM posts WHERE id = ? AND user_id = ?", (post_id, user_id))
    return media


def relative_time(created_at) -> str:
    """Timestamp -> tempo relativo em pt-BR: agora / há X min / há X h / há X d."""
    if not created_at:
        return ""
    delta = int(time.time() - float(created_at))
    if delta < 60:
        return "agora"
    if delta < 3600:
        return f"há {delta // 60} min"
    if delta < 86400:
        return f"há {delta // 3600} h"
    return f"há {delta // 86400} d"


def get_all_posts(current_user_id):
    """Feed completo em UMA consulta (sem N+1) + descriptografia após a busca.

    Os campos protegidos (text_enc, name_enc) só são descriptografados aqui,
    na memória do servidor, já no formato pronto para a interface.
    """
    with _conn() as conn:
        # Contagem de views: registra a visualização ÚNICA deste usuário para
        # cada post de OUTRAS pessoas presente no feed. O INSERT OR IGNORE
        # garante uma view por usuário por post — atualizar o feed não infla
        # o contador (e o próprio autor não contabiliza view nele mesmo).
        conn.execute(
            "INSERT OR IGNORE INTO post_views (post_id, user_id, viewed_at) "
            "SELECT p.id, ?, ? FROM posts p WHERE p.user_id != ?",
            (current_user_id, int(time.time()), current_user_id),
        )
        rows = conn.execute(
            """
            SELECT
                p.id, p.user_id, p.text_enc, p.media, p.created_at,
                u.name_enc, u.profile_pic,
                (SELECT COUNT(*) FROM likes WHERE post_id = p.id)                                 AS likes_count,
                EXISTS (SELECT 1 FROM likes WHERE post_id = p.id AND user_id = ?)                 AS is_liked,
                EXISTS (SELECT 1 FROM followers WHERE follower_id = ? AND following_id = p.user_id) AS is_following,
                (SELECT COUNT(*) FROM followers WHERE following_id = p.user_id)                   AS followers_count,
                (SELECT COUNT(*) FROM post_views WHERE post_id = p.id)                            AS views_count
            FROM posts p
            JOIN users u ON u.id = p.user_id
            ORDER BY p.id DESC
            """,
            (current_user_id, current_user_id),
        ).fetchall()
    feed = []
    for r in rows:
        feed.append(
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "name": decrypt_field(r["name_enc"]) or "Usuário",
                "profile_pic": r["profile_pic"] or DEFAULT_AVATAR,
                "text": decrypt_field(r["text_enc"]),
                "media": r["media"],
                "time_label": relative_time(r["created_at"]),
                "likes_count": r["likes_count"],
                "is_liked": bool(r["is_liked"]),
                "is_following": bool(r["is_following"]),
                "followers_count": r["followers_count"],
                "views_count": r["views_count"],
            }
        )
    return feed
