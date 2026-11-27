"""Utilitários de segurança do Pythomic.

Inclui:
    * criptografia de campos sensíveis (Fernet, com fallback base64);
    * hash e verificação de senhas (PBKDF2-HMAC-SHA256, 600k iterações);
    * hashes determinísticos de busca (HMAC, para name_hash/email_hash);
    * política de senha;
    * limitador de tentativas em memória (RateLimiter).

A separação de domínios entre a chave Fernet e a chave HMAC é mantida:
cada uma deriva de uma "info string" diferente, então comprometer uma
não compromete a outra.
"""

import base64
import hashlib
import hmac
import secrets
import threading
import time

from .config import (
    FIELD_KEY_ITERATIONS,
    MASTER_SECRET,
    PBKDF2_ITERATIONS,
)

# O pacote "cryptography" é opcional: sem ele o app roda em modo de
# contingência (campos gravados em base64). Veja _warn_insecure_fallback.
try:
    from cryptography.fernet import Fernet
    _CRYPTO_OK = True
except ImportError:  # ambiente sem o pacote opcional
    _CRYPTO_OK = False


_CRYPTO_WARNED = False


def _warn_insecure_fallback() -> None:
    """Aviso alto e claro (exibido uma única vez) sobre o modo sem criptografia."""
    global _CRYPTO_WARNED
    if _CRYPTO_WARNED:
        return
    _CRYPTO_WARNED = True
    print("=" * 70)
    print("[Pythomic] AVISO DE SEGURANÇA: o pacote 'cryptography' não está instalado.")
    print("[Pythomic] Os campos sensíveis serão gravados APENAS em base64")
    print("[Pythomic] (ofuscação — NÃO é criptografia de verdade!).")
    print("[Pythomic] Instale com: pip install cryptography")
    print("=" * 70)


def _derive_field_key() -> bytes:
    """Deriva a chave Fernet do segredo mestre.

    base64.urlsafe_b64encode(PBKDF2-HMAC-SHA256(segredo, info
    b"pythomic-field-enc-v1", 200.000 iterações)).
    """
    return base64.urlsafe_b64encode(
        hashlib.pbkdf2_hmac(
            "sha256",
            MASTER_SECRET.encode("utf-8"),
            b"pythomic-field-enc-v1",
            FIELD_KEY_ITERATIONS,
        )
    )


def _derive_lookup_key() -> bytes:
    """Deriva a chave HMAC dos hashes de busca (name_hash / email_hash).

    Usa uma info string DIFERENTE da chave de criptografia (separação de
    domínios): comprometer uma chave não compromete a outra.
    """
    return hashlib.pbkdf2_hmac(
        "sha256",
        MASTER_SECRET.encode("utf-8"),
        b"pythomic-lookup-hmac-v1",
        FIELD_KEY_ITERATIONS,
    )


_FERNET = Fernet(_derive_field_key()) if _CRYPTO_OK else None
_LOOKUP_KEY = _derive_lookup_key()


def encrypt_field(value) -> str:
    """Criptografa um campo sensível (nome, email, texto do post) para o banco.

    Com 'cryptography': Fernet (AES-128-CBC + HMAC-SHA256, autenticado).
    Sem o pacote: prefixo "b64:" + base64 — apenas ofuscação (veja o aviso
    emitido uma vez em _warn_insecure_fallback).
    """
    if value is None:
        return ""
    dados = str(value).encode("utf-8")
    if _FERNET is not None:
        return _FERNET.encrypt(dados).decode("ascii")
    _warn_insecure_fallback()
    return "b64:" + base64.b64encode(dados).decode("ascii")


def decrypt_field(value) -> str:
    """Descriptografa um campo gravado por encrypt_field.

    Aceita valores gravados no modo de contingência ("b64:...") mesmo que o
    'cryptography' já esteja instalado — assim nenhum dado antigo é perdido.
    """
    if not value:
        return ""
    if value.startswith("b64:"):
        try:
            return base64.b64decode(value[4:].encode("ascii")).decode("utf-8")
        except (ValueError, TypeError):
            return ""
    if _FERNET is not None:
        try:
            return _FERNET.decrypt(value.encode("ascii")).decode("utf-8")
        except Exception:
            # Token inválido: o segredo mestre mudou desde a gravação.
            return ""
    return value


def lookup_hash(value) -> str:
    """HMAC-SHA256 determinístico do valor normalizado (para busca/unicidade).

    Guardamos name_hash/email_hash para permitir colunas UNIQUE e consultas
    por igualdade SEM armazenar o dado em texto puro no banco.
    """
    normalizado = (value or "").strip().lower()
    return hmac.new(_LOOKUP_KEY, normalizado.encode("utf-8"), hashlib.sha256).hexdigest()


def hash_password(password: str) -> str:
    """Gera o hash da senha no formato pbkdf2$iterações$salt$hash.

    PBKDF2-HMAC-SHA256 com 600.000 iterações e salt aleatório de 16 bytes.
    """
    salt = secrets.token_hex(16)  # 16 bytes aleatórios (32 caracteres hex)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("ascii"), PBKDF2_ITERATIONS
    )
    return f"pbkdf2${PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verifica a senha com comparação em tempo constante (hmac.compare_digest)."""
    try:
        algo, iteracoes, salt, digest = (stored or "").split("$", 3)
    except ValueError:
        return False
    if algo != "pbkdf2":
        return False
    try:
        iteracoes = int(iteracoes)
    except ValueError:
        return False
    esperado = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("ascii"), iteracoes
    ).hex()
    return hmac.compare_digest(esperado, digest)


def password_policy_error(password: str):
    """Valida a política de senha. Retorna None se válida, ou a mensagem de erro.

    Política: mínimo de 8 caracteres, com pelo menos uma letra e um número.
    Aplicada no cadastro E na troca de senha (a UI também valida, mas a regra
    vale no servidor como defesa adicional).
    """
    senha = password or ""
    if len(senha) < 8:
        return "A senha deve ter pelo menos 8 caracteres."
    if not any(letra.isalpha() for letra in senha):
        return "A senha deve conter pelo menos uma letra."
    if not any(letra.isdigit() for letra in senha):
        return "A senha deve conter pelo menos um número."
    return None


class RateLimiter:
    """Limitador de tentativas em memória, thread-safe (threading.Lock + dict).

    NOTA IMPORTANTE: os componentes ReactPy executam no SERVIDOR — dentro de
    um componente não existe contexto de requisição HTTP acessível (sem IP,
    sem sessão). Por isso o limite de login é chaveado pelo email informado
    ("login:<email>") e o limite de cadastro usa um contador global
    ("register:global").
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._eventos = {}  # chave -> lista de timestamps dentro da janela

    def _podar(self, chave, janela, agora):
        vivos = [quando for quando in self._eventos.get(chave, []) if agora - quando < janela]
        if vivos:
            self._eventos[chave] = vivos
        else:
            self._eventos.pop(chave, None)
        return vivos

    def hit(self, chave, limite, janela):
        """Registra uma tentativa. Retorna (permitido, segundos_para_liberar)."""
        agora = time.time()
        with self._lock:
            eventos = self._podar(chave, janela, agora)
            if len(eventos) >= limite:
                return False, max(1, int(janela - (agora - eventos[0])))
            eventos.append(agora)
            self._eventos[chave] = eventos
            return True, 0

    def reset(self, chave):
        """Limpa o histórico da chave (ex.: após um login bem-sucedido)."""
        with self._lock:
            self._eventos.pop(chave, None)


rate_limiter = RateLimiter()
