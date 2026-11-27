"""Bot de email do Pythomic.

Responsabilidades:
    * validar se um email é real (formato + domínio com registro MX);
    * gerar códigos de verificação (confirmação de email no cadastro);
    * gerar senhas aleatórias (recuperação de senha);
    * enviar tudo por SMTP.

Configuração via VARIÁVEIS DE AMBIENTE (o usuário configura com a própria
conta de email — o Pythomic NÃO traz credenciais embutidas):

    SMTP_HOST     — servidor (ex.: smtp.gmail.com)
    SMTP_PORT     — porta (587 p/ STARTTLS, 465 p/ SSL)
    SMTP_USER     — login do remetente (ex.: voce@gmail.com)
    SMTP_PASS     — senha de app (NUNCA a senha principal da conta)
    SMTP_FROM     — remetente (opcional; padrão = SMTP_USER)
    SMTP_SECURE   — "ssl" (porta 465) ou "starttls" (porta 587); padrão starttls

SEM essas variáveis o bot roda em MODO DEV: em vez de enviar, grava o
código/senha no log (stderr) e devolve o valor — assim o fluxo de cadastro e
recuperação continua testável mesmo sem um servidor de email configurado.
"""

import os
import re
import secrets
import smtplib
import ssl
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Formato de email: aceita os provedores comuns (gmail, hotmail, outlook,
# yahoo, proton, etc.) — NÃO há whitelist de domínio. Só rejeita sintaxe
# claramente inválida.
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

# dnspython permite checar registros MX (prova que o domínio recebe email).
# Se não estiver instalado, o passo de domínio é pulado (a prova real vem do
# código enviado por email).
try:
    import dns.resolver
    _DNS_OK = True
except ImportError:  # ambiente sem o pacote opcional
    _DNS_OK = False

_APP_NAME = "Pythomic"


def is_valid_email(addr):
    """Verifica se o email é real: formato válido + domínio com registro MX.

    Aceita TODOS os provedores (gmail, hotmail, outlook, etc.) — não há
    whitelist. Retorna (True, "") se válido, ou (False, "motivo em pt-BR").

    Só REJEITA de fato quando o domínio não existe (NXDOMAIN). Falhas de rede
    ou ausência de MX não bloqueiam o cadastro: a confirmação real de que o
    email existe/recebe mensagem é o CÓDIGO enviado por email no passo
    seguinte (defesa em profundidade).
    """
    addr = (addr or "").strip()
    if not addr:
        return False, "Informe um email."
    if len(addr) > 120:
        return False, "Email muito longo (máximo 120 caracteres)."
    if not _EMAIL_RE.match(addr):
        return False, "Email inválido. Verifique se o endereço está correto."
    if not _DNS_OK:
        # Sem dnspython: aceita (o código por email é a verificação real).
        return True, ""
    dominio = addr.rsplit("@", 1)[1].lower()
    try:
        dns.resolver.resolve(dominio, "MX")
        return True, ""
    except dns.resolver.NXDOMAIN:
        # Domínio realmente não existe — email certamente falso.
        return False, "O domínio do email não existe. Verifique se o endereço está correto."
    except Exception:
        # Sem MX, timeout, etc.: não bloqueia — a prova real é o código por email.
        return True, ""


def generate_code():
    """Código de verificação de 6 dígitos (string, preserva zeros à esquerda)."""
    return f"{secrets.randbelow(1_000_000):06d}"


def generate_password():
    """Senha aleatória forte (12 caracteres, letras + dígitos).

    Atende à política do Pythomic (mín. 8, com letra e número). Usa
    secrets (CSPRNG) e um alfabeto sem caracteres ambíguos (0/O, 1/l).
    """
    letras = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz"
    digitos = "23456789"
    alfabeto = letras + digitos
    rng = secrets.SystemRandom()
    # Garante pelo menos uma letra e um dígito.
    senha = [secrets.choice(letras), secrets.choice(digitos)]
    senha += [secrets.choice(alfabeto) for _ in range(10)]
    rng.shuffle(senha)
    return "".join(senha)


def _smtp_config():
    """Lê a config SMTP do ambiente. Retorna dict ou None (modo dev)."""
    host = os.environ.get("SMTP_HOST", "").strip()
    if not host:
        return None
    try:
        porta = int(os.environ.get("SMTP_PORT", "587"))
    except ValueError:
        porta = 587
    user = os.environ.get("SMTP_USER", "").strip()
    return {
        "host": host,
        "port": porta,
        "user": user,
        "password": os.environ.get("SMTP_PASS", ""),
        "from": os.environ.get("SMTP_FROM", user).strip() or user,
        "secure": os.environ.get("SMTP_SECURE", "starttls").strip().lower(),
    }


def send_email(to_addr, subject, body):
    """Envia um email em texto puro via SMTP. Retorna True se enviado.

    Sem SMTP configurado (modo dev): grava a mensagem no stderr e devolve
    True, para o fluxo (cadastro/recuperação) continuar testável.
    """
    cfg = _smtp_config()
    if cfg is None:
        # MODO DEV: o "envio" vira log. Nada sai do sandbox.
        print(
            f"[MAILER DEV] Para: {to_addr} | Assunto: {subject}\n{body}",
            file=sys.stderr,
            flush=True,
        )
        return True
    msg = MIMEMultipart("alternative")
    msg["From"] = cfg["from"]
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        if cfg["secure"] == "ssl":
            with smtplib.SMTP_SSL(
                cfg["host"], cfg["port"], context=ssl.create_default_context(), timeout=15
            ) as s:
                if cfg["user"]:
                    s.login(cfg["user"], cfg["password"])
                s.sendmail(cfg["from"], [to_addr], msg.as_string())
        else:  # starttls (padrão)
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=15) as s:
                s.ehlo()
                s.starttls(context=ssl.create_default_context())
                s.ehlo()
                if cfg["user"]:
                    s.login(cfg["user"], cfg["password"])
                s.sendmail(cfg["from"], [to_addr], msg.as_string())
        return True
    except Exception as exc:
        print(f"[MAILER] Falha ao enviar para {to_addr}: {exc}", file=sys.stderr, flush=True)
        return False


def send_verification_code(to_addr, code):
    """Envia o código de verificação do cadastro."""
    body = (
        f"Olá!\n\n"
        f"Seu código de verificação no {_APP_NAME} é: {code}\n\n"
        f"Digite esse código na tela de cadastro para confirmar seu email.\n"
        f"Se você não criou uma conta, ignore esta mensagem.\n"
    )
    return send_email(to_addr, f"{_APP_NAME} — seu código de verificação", body)


def send_new_password(to_addr, password):
    """Envia a nova senha gerada na recuperação de senha."""
    body = (
        f"Olá!\n\n"
        f"Você pediu a recuperação da sua senha no {_APP_NAME}.\n"
        f"Sua nova senha é: {password}\n\n"
        f"Use-a para entrar normalmente — o site funciona igual ao login de "
        f"sempre. Recomendamos trocar essa senha nas Configurações assim que "
        f"entrar.\n\n"
        f"Se você não pediu a recuperação, entre e troque sua senha: alguém "
        f"pode estar tentando acessar sua conta.\n"
    )
    return send_email(to_addr, f"{_APP_NAME} — sua nova senha", body)
