"""Modal do perfil próprio: foto, estatísticas (+ views), senha, tema e logout."""

import time

from reactpy import component, event, html, use_state

from ...database import (
    delete_user,
    get_user_by_id,
    get_user_stats,
    login_user,
    safe_user,
    update_password,
    update_profile_pic,
)
from ...security import password_policy_error
from ...uploads import UploadError, delete_media, save_media
from ..icons import IconCamera, IconClose, IconEye, IconEyeOff, IconLogout, IconMoon, IconSun, IconTrash
from ..scripts import AVATAR_UPLOAD_SCRIPT


@component
def MenuModal(user, set_user, is_dark, set_is_dark, on_close, refresh):
    """Menu do perfil: foto, estatísticas (+ views), senha, tema e logout."""
    stats = get_user_stats(user["id"])
    old_pwd, set_old_pwd = use_state("")
    new_pwd, set_new_pwd = use_state("")
    conf_pwd, set_conf_pwd = use_state("")
    pwd_msg, set_pwd_msg = use_state("")
    pwd_ok, set_pwd_ok = use_state(False)
    show_pwd, set_show_pwd = use_state(False)
    avatar_data, set_avatar_data = use_state(None)
    avatar_key, set_avatar_key = use_state(0)
    avatar_msg, set_avatar_msg = use_state("")
    avatar_ok, set_avatar_ok = use_state(False)
    # Exclusão de conta: passo 0 (botão), 1 (1ª confirmação), 2 (digitar EXCLUIR).
    del_step, set_del_step = use_state(0)
    del_text, set_del_text = use_state("")
    del_msg, set_del_msg = use_state("")

    def toggle_theme(e):
        # Troca o estado no servidor; o script de sincronização (keyed)
        # aplica o data-theme no <html> e grava no localStorage.
        set_is_dark(not is_dark)

    def change_avatar(e):
        """Troca a foto de perfil: valida (somente imagens), grava e atualiza a UI."""
        set_avatar_msg("")
        set_avatar_ok(False)
        if not avatar_data:
            set_avatar_msg("Escolha uma imagem primeiro.")
            return
        try:
            caminho = save_media(
                avatar_data, f"avatar_{user['id']}_{int(time.time())}", images_only=True
            )
        except UploadError as err:
            set_avatar_msg(str(err))
            return
        update_profile_pic(user["id"], caminho)
        # safe_user() de novo: a nova foto sai limpa para toda a interface.
        set_user(safe_user(get_user_by_id(user["id"])))
        set_avatar_data(None)
        set_avatar_key(lambda k: k + 1)  # reseta o input de arquivo
        set_avatar_ok(True)
        set_avatar_msg("Foto de perfil atualizada!")
        refresh()  # propaga a nova foto para os cards do feed

    def change_password(e):
        set_pwd_msg("")
        set_pwd_ok(False)
        # Mesma política do cadastro: 8+ caracteres, letra e número.
        erro_politica = password_policy_error(new_pwd)
        if erro_politica:
            set_pwd_msg(erro_politica)
            return
        if new_pwd != conf_pwd:
            set_pwd_msg("A nova senha e a confirmação não conferem.")
            return
        if not login_user(user["name"], old_pwd):
            set_pwd_msg("Senha atual incorreta.")
            return
        update_password(user["id"], new_pwd)
        set_pwd_ok(True)
        set_pwd_msg("Senha alterada com sucesso!")
        set_old_pwd("")
        set_new_pwd("")
        set_conf_pwd("")

    def handle_delete_account(e):
        set_del_msg("")
        if del_text.strip().upper() != "EXCLUIR":
            set_del_msg("Digite EXCLUIR exatamente para confirmar.")
            return
        # Apaga a conta + todos os dados; a mídia do disco é removida em seguida.
        midias = delete_user(user["id"])
        for caminho in midias:
            delete_media(caminho)
        # set_user(None) desmonta a Home (App cai no WelcomeScreen) — desloga.
        set_user(None)

    tipo_senha = "text" if show_pwd else "password"

    return html.div(
        {"class": "py-overlay", "on_click": on_close},
        html.div(
            {"class": "py-modal", "on_click": event(lambda e: None, stop_propagation=True)},
            html.button(
                {"class": "py-icon-btn py-modal-close", "on_click": on_close, "title": "Fechar"},
                IconClose(20),
            ),
            html.h3({"class": "py-modal-title"}, f"@{user['name']}"),
            html.div(
                {"class": "py-avatar-wrap"},
                html.div(
                    {"class": "py-avatar py-avatar-lg"},
                    html.img({"src": user["profile_pic"], "alt": user["name"]}),
                ),
            ),
            html.input(
                {
                    "type": "file",
                    "id": "py_avatar_file_input",
                    "key": f"avatar-file-{avatar_key}",
                    "class": "py-input py-file",
                    "accept": "image/jpeg,image/png,image/gif,image/webp",
                }
            ),
            html.input(
                {
                    "type": "hidden",
                    "id": "py_avatar_b64_input",
                    "key": f"avatar-hidden-{avatar_key}",
                    "on_change": lambda e: set_avatar_data(e["target"]["value"]),
                }
            ),
            html.img(
                {
                    "src": avatar_data,
                    "class": "py-thumb",
                    "alt": "Pré-visualização da nova foto",
                }
            ) if avatar_data and avatar_data.startswith("data:image") else None,
            html.button(
                {"class": "py-btn py-btn-primary", "on_click": change_avatar},
                IconCamera(18),
                "Salvar Nova Foto",
            ),
            html.div(
                {"class": "py-success" if avatar_ok else "py-error"}, avatar_msg
            ) if avatar_msg else None,
            html.div(
                {"class": "py-stats"},
                html.span(
                    {"class": "py-stat"},
                    html.strong({}, str(stats["followers"])),
                    "seguidores",
                ),
                html.span(
                    {"class": "py-stat"},
                    html.strong({}, str(stats["following"])),
                    "seguindo",
                ),
                html.span(
                    {"class": "py-stat"},
                    html.strong({}, str(stats["posts"])),
                    "posts",
                ),
                html.span(
                    {"class": "py-stat"},
                    html.strong({}, str(stats["views"])),
                    "views",
                ),
            ),
            html.hr({"class": "py-divider"}),
            html.h4({"class": "py-section-title"}, "Trocar Senha"),
            html.input(
                {
                    "class": "py-input",
                    "type": "password",
                    "placeholder": "Senha atual",
                    "value": old_pwd,
                    "on_change": lambda e: set_old_pwd(e["target"]["value"]),
                }
            ),
            html.div(
                {"class": "py-pwd-row"},
                html.input(
                    {
                        "class": "py-input",
                        "type": tipo_senha,
                        "placeholder": "Nova senha",
                        "value": new_pwd,
                        "on_change": lambda e: set_new_pwd(e["target"]["value"]),
                    }
                ),
                html.button(
                    {
                        "class": "py-icon-btn py-pwd-toggle",
                        "type": "button",
                        "on_click": lambda e: set_show_pwd(not show_pwd),
                        "title": "Ocultar senha" if show_pwd else "Mostrar senha",
                    },
                    IconEyeOff(20) if show_pwd else IconEye(20),
                ),
            ),
            html.input(
                {
                    "class": "py-input",
                    "type": tipo_senha,
                    "placeholder": "Confirmar nova senha",
                    "value": conf_pwd,
                    "on_change": lambda e: set_conf_pwd(e["target"]["value"]),
                }
            ),
            html.p(
                {"class": "py-hint"},
                "Mínimo de 8 caracteres, com pelo menos uma letra e um número.",
            ),
            html.button({"class": "py-btn py-btn-primary", "on_click": change_password},
                        "Alterar Senha"),
            html.div(
                {"class": "py-success" if pwd_ok else "py-error"},
                pwd_msg,
            ) if pwd_msg else None,
            html.hr({"class": "py-divider"}),
            html.button(
                {"class": "py-btn py-btn-outline", "on_click": toggle_theme},
                IconMoon(18) if not is_dark else IconSun(18),
                f"Trocar para {'Light Mode' if is_dark else 'Dark Mode'}",
            ),
            html.button(
                {"class": "py-btn py-btn-danger", "on_click": lambda e: set_user(None)},
                IconLogout(18),
                "Sair da Conta",
            ),
            html.hr({"class": "py-divider"}),
            html.h4({"class": "py-section-title"}, "Zona de perigo"),
            # Passo 0: botão que abre a exclusão.
            html.button(
                {
                    "class": "py-btn py-btn-danger",
                    "on_click": lambda e: (set_del_step(1), set_del_msg(""), set_del_text("")),
                },
                IconTrash(18),
                "Excluir conta",
            ) if del_step == 0 else None,
            # Passo 1: primeira confirmação + aviso de que NÃO dá para recuperar.
            html.div(
                {"class": "py-confirm-box py-danger-zone"},
                html.p(
                    {"style": {"margin": "0 0 6px", "fontWeight": "700", "color": "var(--danger)"}},
                    "Tem certeza?",
                ),
                html.p(
                    {"class": "py-hint", "style": {"textAlign": "left", "margin": "0 0 12px"}},
                    "Esta ação NÃO pode ser desfeita. Todos os seus posts, fotos, "
                    "curtidas e dados serão apagados permanentemente. Não haverá "
                    "como recuperar a conta depois.",
                ),
                html.button(
                    {"class": "py-btn py-btn-danger", "on_click": lambda e: set_del_step(2)},
                    "Sim, continuar",
                ),
                html.button(
                    {"class": "py-btn py-btn-ghost", "on_click": lambda e: set_del_step(0)},
                    "Cancelar",
                ),
            ) if del_step == 1 else None,
            # Passo 2: digitar EXCLUIR para apagar definitivamente (2ª confirmação).
            html.div(
                {"class": "py-confirm-box py-danger-zone"},
                html.p(
                    {"style": {"margin": "0 0 6px", "fontWeight": "700", "color": "var(--danger)"}},
                    "Última chance",
                ),
                html.p(
                    {"class": "py-hint", "style": {"textAlign": "left", "margin": "0 0 12px"}},
                    "Digite EXCLUIR para apagar sua conta definitivamente.",
                ),
                html.input(
                    {
                        "class": "py-input",
                        "type": "text",
                        "placeholder": "Digite EXCLUIR",
                        "value": del_text,
                        "on_change": lambda e: set_del_text(e["target"]["value"]),
                    }
                ),
                html.div({"class": "py-error"}, del_msg) if del_msg else None,
                html.button(
                    {"class": "py-btn py-btn-danger", "on_click": handle_delete_account},
                    IconTrash(18),
                    "Apagar conta definitivamente",
                ),
                html.button(
                    {"class": "py-btn py-btn-ghost", "on_click": lambda e: set_del_step(0)},
                    "Cancelar",
                ),
            ) if del_step == 2 else None,
            # Religa o listener do input de arquivo da foto: a key muda junto
            # com avatar_key e o script é remontado a cada reset (mesmo padrão
            # do modal de criação de post).
            html.script({"key": f"avatar-script-{avatar_key}"}, AVATAR_UPLOAD_SCRIPT),
        ),
    )
