"""Configuração, caminhos e segredos do Pythomic.

Tudo que é constante ou caminho de arquivo vive aqui, separado da lógica.
O segredo mestre (que deriva as chaves de criptografia) é obtido com a
mesma política da versão original:
    1. variável de ambiente PYTHOMIC_SECRET;
    2. arquivo ".pythomic_secret" (0600), criado na primeira execução.
"""

import base64
import hashlib
import os
import secrets

# ==================== CAMINHOS ====================
# Base do projeto: a pasta onde run.py está. Usamos o diretório do pacote
# "pythomic" e subimos um nível para chegar à raiz do projeto.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_NAME = os.path.join(_BASE_DIR, "database.db")
UPLOAD_DIR = os.path.join(_BASE_DIR, "uploads")
SECRET_FILE = os.path.join(_BASE_DIR, ".pythomic_secret")

# ==================== PARÂMETROS DE SEGURANÇA ====================
PBKDF2_ITERATIONS = 600_000            # hash de senha (recomendação atual p/ SHA-256)
FIELD_KEY_ITERATIONS = 200_000         # derivação das chaves de campo (Fernet/HMAC)
MAX_FILE_SIZE = 10 * 1024 * 1024       # 10 MB por upload
MAX_CONTENT_LENGTH = 12 * 1024 * 1024  # limite do corpo HTTP aceito pelo Flask
MAX_POST_LENGTH = 500                  # tamanho máximo do texto do post

# ==================== RATE LIMITING (limites em memória) ====================
LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW = 15 * 60                 # 15 minutos
REGISTER_MAX_PER_HOUR = 30
REGISTER_WINDOW = 60 * 60              # 1 hora

# ==================== EMAIL / RECUPERAÇÃO DE SENHA ====================
VERIFY_CODE_EXPIRY = 15 * 60           # código de verificação de email expira em 15 min
RECOVERY_MAX_PER_HOUR = 5              # tentativas de recuperação por email por hora
RECOVERY_WINDOW = 60 * 60              # janela de 1 hora

# Avatar padrão embutido (SVG em data URI — nada é enviado a servidores externos)
DEFAULT_AVATAR = (
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' "
    "fill='%23dbdbdb'><path d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4z"
    "m0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/></svg>"
)


def _load_master_secret() -> str:
    """Obtém o segredo mestre usado para derivar as chaves de criptografia.

    Prioridade:
      1. Variável de ambiente PYTHOMIC_SECRET;
      2. Arquivo ".pythomic_secret" — criado na primeira execução com
         permissão 0600 caso não exista, e recarregado nas seguintes.
    """
    segredo = os.environ.get("PYTHOMIC_SECRET", "").strip()
    if segredo:
        return segredo
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "r", encoding="utf-8") as arquivo:
            segredo = arquivo.read().strip()
        if segredo:
            return segredo
        # Arquivo existe mas está VAZIO: trata como primeira execução e
        # reescreve com um segredo novo (criptografar com "" seria catastrófico).
        segredo = secrets.token_urlsafe(32)
        with open(SECRET_FILE, "w", encoding="utf-8") as arquivo:
            arquivo.write(segredo)
        try:
            os.chmod(SECRET_FILE, 0o600)  # reforça a permissão do arquivo antigo
        except OSError:
            pass
        return segredo
    # Primeira execução (arquivo inexistente): cria com 0600 atomicamente para
    # não deixar o segredo world-readable nem entre a criação e o chmod.
    segredo = secrets.token_urlsafe(32)
    descritor = os.open(SECRET_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descritor, "w", encoding="utf-8") as arquivo:
        arquivo.write(segredo)
    return segredo


MASTER_SECRET = _load_master_secret()
