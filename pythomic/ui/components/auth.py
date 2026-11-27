"""Tela de autenticação: login por nome, cadastro com verificação de email
(código enviado pelo bot) e recuperação de senha (nova senha gerada e enviada
por email).
"""

from reactpy import component, html, use_state

from ...config import (
    LOGIN_MAX_ATTEMPTS,
    LOGIN_WINDOW,
    RECOVERY_MAX_PER_HOUR,
    RECOVERY_WINDOW,
    REGISTER_MAX_PER_HOUR,
    REGISTER_WINDOW,
)
from ...database import (
    create_pending_registration,
    get_user_by_id,
    login_user,
    recover_password,
    resend_verification_code,
    safe_user,
    verify_pending_registration,
)
from ...mailer import is_valid_email, send_new_password, send_verification_code
from ...security import password_policy_error, rate_limiter
from ..icons import IconEye, IconEyeOff, IconMail


@component
def AuthScreen(set_page, set_user):
    """Login por nome de usuário, cadastro com confirmação de email e
    recuperação de senha por email."""
    # login | register | verify | recover
    mode, set_mode = use_state("login")
    name, set_name = use_state("")
    email, set_email = use_state("")
    pwd, set_pwd = use_state("")
    conf, set_conf = use_state("")
    code, set_code = use_state("")
    error, set_error = use_state("")
    msg, set_msg = use_state("")
    show_pwd, set_show_pwd = use_state(False)
    pending_email, set_pending_email = use_state("")

    def go(novo):
        set_error("")
        set_msg("")
        set_mode(novo)

    def handle_login(e):
        set_error("")
        set_msg("")
        nome = name.strip()
        if not nome or not pwd:
            set_error("Informe nome de usuário e senha.")
            return
        # Rate limit de login: 5 tentativas por 15 min por nome de usuário.
        chave = f"login:{nome.lower()}"
        permitido, espera = rate_limiter.hit(chave, LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW)
        if not permitido:
            set_error(f"Muitas tentativas. Tente novamente em {max(1, espera // 60)} minuto(s).")
            return
        usuario = login_user(nome, pwd)
        if usuario:
            rate_limiter.reset(chave)  # sucesso limpa o histórico de falhas
            # safe_user() garante que o hash da senha NUNCA chega à interface.
            set_user(safe_user(usuario))
            set_page("home")
        else:
            set_error("Nome de usuário ou senha inválidos.")

    def handle_register(e):
        set_error("")
        set_msg("")
        nome = name.strip()
        email_norm = email.strip().lower()
        if not nome:
            set_error("Informe um nome de usuário.")
            return
        if len(nome) > 30:
            set_error("O nome de usuário deve ter no máximo 30 caracteres.")
            return
        # Verificação de email real (formato + domínio com MX). Aceita todos os
        # provedores (gmail, hotmail, outlook...); rejeita só sintaxe inválida
        # ou domínio que não existe.
        ok, motivo = is_valid_email(email_norm)
        if not ok:
            set_error(motivo)
            return
        erro_politica = password_policy_error(pwd)
        if erro_politica:
            set_error(erro_politica)
            return
        if pwd != conf:
            set_error("As senhas não conferem.")
            return
        permitido, espera = rate_limiter.hit(
            "register:global", REGISTER_MAX_PER_HOUR, REGISTER_WINDOW
        )
        if not permitido:
            set_error(f"Muitos cadastros neste momento. Tente novamente em {max(1, espera // 60)} minuto(s).")
            return
        # Cria cadastro PENDENTE e devolve o código; o bot envia por email.
        codigo = create_pending_registration(nome, email_norm, pwd)
        if not codigo:
            set_error("Nome de usuário ou email já cadastrados.")
            return
        send_verification_code(email_norm, codigo)
        set_pending_email(email_norm)
        set_code("")
        set_msg(f"Enviamos um código de 6 dígitos para {email_norm}.")
        set_mode("verify")

    def handle_verify(e):
        set_error("")
        set_msg("")
        if not code.strip():
            set_error("Digite o código de 6 dígitos.")
            return
        uid = verify_pending_registration(pending_email, code.strip())
        if uid:
            set_user(safe_user(get_user_by_id(uid)))
            set_page("home")
        else:
            set_error("Código inválido ou expirado.")

    def handle_resend(e):
        set_error("")
        set_msg("")
        codigo = resend_verification_code(pending_email)
        if codigo:
            send_verification_code(pending_email, codigo)
            set_msg("Reenviamos o código para seu email.")
        else:
            set_error("Não há cadastro pendente para esse email.")

    def handle_recover(e):
        set_error("")
        set_msg("")
        email_norm = email.strip().lower()
        ok, motivo = is_valid_email(email_norm)
        if not ok:
            set_error(motivo)
            return
        # Rate limit de recuperação: 5 por hora por email.
        chave = f"recovery:{email_norm}"
        permitido, espera = rate_limiter.hit(chave, RECOVERY_MAX_PER_HOUR, RECOVERY_WINDOW)
        if not permitido:
            set_error(f"Muitas tentativas. Tente novamente em {max(1, espera // 60)} minuto(s).")
            return
        encontrado, nova = recover_password(email_norm)
        if encontrado:
            send_new_password(email_norm, nova)
            set_msg(
                "Geramos uma nova senha e enviamos para seu email. Use-a para "
                "entrar — o site funciona igual ao login normal. Depois você "
                "pode trocá-la nas Configurações."
            )
        else:
            set_error("Nenhuma conta encontrada com esse email.")

    tipo_senha = "text" if show_pwd else "password"

    def olho_btn():
        return html.button(
            {
                "class": "py-icon-btn py-pwd-toggle",
                "type": "button",
                "on_click": lambda e: set_show_pwd(not show_pwd),
                "title": "Ocultar senha" if show_pwd else "Mostrar senha",
            },
            IconEyeOff(20) if show_pwd else IconEye(20),
        )

    titulos = {
        "login": "Entrar",
        "register": "Criar Conta",
        "verify": "Verifique seu email",
        "recover": "Recuperar senha",
    }

    campos = []
    botoes = []

    if mode == "login":
        campos.append(html.input(
            {
                "class": "py-input",
                "type": "text",
                "placeholder": "Nome de usuário",
                "value": name,
                "maxLength": 30,
                "on_change": lambda e: set_name(e["target"]["value"]),
            }
        ))
        campos.append(html.div(
            {"class": "py-pwd-row"},
            html.input(
                {
                    "class": "py-input",
                    "type": tipo_senha,
                    "placeholder": "Senha",
                    "value": pwd,
                    "on_change": lambda e: set_pwd(e["target"]["value"]),
                }
            ),
            olho_btn(),
        ))
        botoes.append(html.button(
            {"class": "py-btn py-btn-primary", "on_click": handle_login}, "Entrar"
        ))
        botoes.append(html.button(
            {"class": "py-btn py-btn-ghost", "on_click": lambda e: go("register")}, "Criar conta"
        ))
        botoes.append(html.button(
            {"class": "py-link", "on_click": lambda e: go("recover")}, "Esqueci minha senha"
        ))
        botoes.append(html.button(
            {"class": "py-btn py-btn-ghost", "on_click": lambda e: set_page("welcome")}, "Voltar"
        ))

    elif mode == "register":
        campos.append(html.input(
            {
                "class": "py-input",
                "type": "text",
                "placeholder": "Nome de usuário",
                "value": name,
                "maxLength": 30,
                "on_change": lambda e: set_name(e["target"]["value"]),
            }
        ))
        campos.append(html.input(
            {
                "class": "py-input",
                "type": "email",
                "placeholder": "Email (gmail, hotmail, outlook...)",
                "value": email,
                "on_change": lambda e: set_email(e["target"]["value"]),
            }
        ))
        campos.append(html.div(
            {"class": "py-pwd-row"},
            html.input(
                {
                    "class": "py-input",
                    "type": tipo_senha,
                    "placeholder": "Senha",
                    "value": pwd,
                    "on_change": lambda e: set_pwd(e["target"]["value"]),
                }
            ),
            olho_btn(),
        ))
        campos.append(html.input(
            {
                "class": "py-input",
                "type": tipo_senha,
                "placeholder": "Confirmar Senha",
                "value": conf,
                "on_change": lambda e: set_conf(e["target"]["value"]),
            }
        ))
        campos.append(html.p(
            {"class": "py-hint"},
            "Mínimo de 8 caracteres, com letra e número. Você confirmará o email com um código.",
        ))
        botoes.append(html.button(
            {"class": "py-btn py-btn-primary", "on_click": handle_register}, "Criar Conta"
        ))
        botoes.append(html.button(
            {"class": "py-btn py-btn-ghost", "on_click": lambda e: go("login")}, "Fazer Login"
        ))
        botoes.append(html.button(
            {"class": "py-btn py-btn-ghost", "on_click": lambda e: set_page("welcome")}, "Voltar"
        ))

    elif mode == "verify":
        campos.append(html.p(
            {"class": "py-auth-subtitle"},
            f"Enviamos um código de 6 dígitos para {pending_email}. Digite-o para "
            f"confirmar seu email e ativar a conta.",
        ))
        campos.append(html.input(
            {
                "class": "py-input py-code-input",
                "type": "text",
                "inputMode": "numeric",
                "placeholder": "Código de 6 dígitos",
                "value": code,
                "maxLength": 6,
                "on_change": lambda e: set_code(e["target"]["value"]),
            }
        ))
        botoes.append(html.button(
            {"class": "py-btn py-btn-primary", "on_click": handle_verify}, "Verificar"
        ))
        botoes.append(html.button(
            {"class": "py-btn py-btn-ghost", "on_click": handle_resend}, "Reenviar código"
        ))
        botoes.append(html.button(
            {"class": "py-btn py-btn-ghost", "on_click": lambda e: go("register")}, "Voltar"
        ))

    elif mode == "recover":
        campos.append(html.p(
            {"class": "py-auth-subtitle"},
            "Digite o email da sua conta. Vamos gerar uma nova senha aleatória e "
            "enviar para esse email. Depois, entre normalmente — o site funciona "
            "igual ao login de sempre. Você pode trocar a senha nas Configurações.",
        ))
        campos.append(html.input(
            {
                "class": "py-input",
                "type": "email",
                "placeholder": "Email da conta",
                "value": email,
                "on_change": lambda e: set_email(e["target"]["value"]),
            }
        ))
        botoes.append(html.button(
            {"class": "py-btn py-btn-primary", "on_click": handle_recover},
            IconMail(18),
            "Enviar nova senha",
        ))
        botoes.append(html.button(
            {"class": "py-btn py-btn-ghost", "on_click": lambda e: go("login")}, "Voltar para login"
        ))

    return html.div(
        {"class": "py-auth"},
        html.div({"class": "py-logo py-auth-logo"}, "Pythomic"),
        html.h2({"class": "py-auth-title"}, titulos[mode]),
        html.div({"class": "py-error"}, error) if error else None,
        html.div({"class": "py-success"}, msg) if msg else None,
        *campos,
        *botoes,
    )
