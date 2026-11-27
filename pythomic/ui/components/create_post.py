"""Modal (bottom sheet) de criação de post: texto + mídia (padrão base64)."""

import time

from reactpy import component, event, html, use_state

from ...config import MAX_POST_LENGTH
from ...database import create_post
from ...uploads import UploadError, save_media
from ..icons import IconCheck, IconClose
from ..scripts import FILE_UPLOAD_SCRIPT


@component
def CreatePostModal(user, on_close, refresh):
    """Modal de criação de post: texto + mídia (padrão base64 do projeto)."""
    post_text, set_post_text = use_state("")
    file_data, set_file_data = use_state(None)
    upload_key, set_upload_key = use_state(0)
    post_error, set_post_error = use_state("")

    restantes = MAX_POST_LENGTH - len(post_text)

    def handle_publish(e):
        text = post_text.strip()
        if not text and not file_data:
            set_post_error("Escreva algo ou anexe uma mídia.")
            return
        media_path = None
        if file_data:
            try:
                media_path = save_media(file_data, f"post_{user['id']}_{int(time.time())}")
            except UploadError as err:
                set_post_error(str(err))
                return
        create_post(user["id"], text, media_path)
        set_post_text("")
        set_file_data(None)
        set_post_error("")
        set_upload_key(lambda k: k + 1)  # reseta o input de arquivo
        refresh()
        on_close(e)

    preview = None
    if file_data and file_data.startswith("data:image"):
        preview = html.img(
            {"src": file_data, "class": "py-thumb", "alt": "Pré-visualização da mídia"}
        )

    return html.div(
        {"class": "py-overlay", "on_click": on_close},
        html.div(
            {"class": "py-modal", "on_click": event(lambda e: None, stop_propagation=True)},
            html.button(
                {"class": "py-icon-btn py-modal-close", "on_click": on_close, "title": "Fechar"},
                IconClose(20),
            ),
            html.h3({"class": "py-modal-title"}, "Criar Post"),
            html.textarea(
                {
                    "class": "py-input py-textarea",
                    "placeholder": "Escreva um texto...",
                    "value": post_text,
                    "maxLength": MAX_POST_LENGTH,
                    "on_change": lambda e: set_post_text(e["target"]["value"]),
                }
            ),
            html.div(
                {"class": "py-counter" + ("" if restantes > 0 else " py-counter-full")},
                f"{restantes} caracteres restantes",
            ),
            html.input(
                {
                    "type": "file",
                    "id": "py_file_input",
                    "key": f"file-{upload_key}",
                    "class": "py-input py-file",
                    "accept": "image/jpeg,image/png,image/gif,image/webp,video/mp4",
                }
            ),
            html.input(
                {
                    "type": "hidden",
                    "id": "py_base64_input",
                    "key": f"hidden-{upload_key}",
                    "on_change": lambda e: set_file_data(e["target"]["value"]),
                }
            ),
            preview,
            html.p({"class": "py-attached"}, IconCheck(14), "Mídia anexada") if file_data else None,
            html.div({"class": "py-error"}, post_error) if post_error else None,
            html.button(
                {"class": "py-btn py-btn-primary", "on_click": handle_publish,
                 "style": {"marginBottom": "14px"}},
                "Publicar",
            ),
            # A key muda junto com upload_key: o script é remontado e religa
            # o listener no novo input de arquivo a cada reset.
            html.script({"key": f"upload-script-{upload_key}"}, FILE_UPLOAD_SCRIPT),
        ),
    )
