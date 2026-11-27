"""Modal do perfil de outro usuário (abre ao clicar no avatar/nome de um post)."""

import time

from reactpy import component, event, html, use_state

from ...database import (
    get_user_by_id,
    get_user_stats,
    is_following,
    safe_user,
    toggle_follow,
)
from ..icons import IconClose


@component
def ProfileModal(current_user, profile_id, on_close, refresh):
    """Perfil de um usuário: foto, estatísticas e botão Seguir ao lado.

    Abre ao clicar no perfil (avatar/nome) de qualquer card do feed. O botão
    Seguir/Seguindo fica AO LADO do perfil, como no Instagram; no próprio
    perfil ele não aparece — ficam só as estatísticas.
    """
    dados = safe_user(get_user_by_id(profile_id)) if profile_id else None
    stats = get_user_stats(profile_id) if profile_id else None
    seguindo, set_seguindo = use_state(
        is_following(current_user["id"], profile_id) if profile_id else False
    )
    seguidores, set_seguidores = use_state(stats["followers"] if stats else 0)

    def toggle_follow_click(e):
        agora_segue = toggle_follow(current_user["id"], profile_id)
        set_seguindo(agora_segue)
        set_seguidores(lambda n: n + (1 if agora_segue else -1))
        refresh()  # mantém os botões "Seguir" dos cards em sincronia

    if dados is None or stats is None:
        return html.div(
            {"class": "py-overlay", "on_click": on_close},
            html.div(
                {"class": "py-modal", "on_click": event(lambda e: None, stop_propagation=True)},
                html.button(
                    {"class": "py-icon-btn py-modal-close", "on_click": on_close,
                     "title": "Fechar"},
                    IconClose(20),
                ),
                html.p({"class": "py-modal-sub"}, "Perfil não encontrado."),
            ),
        )

    botao_seguir = None
    if dados["id"] != current_user["id"]:
        botao_seguir = html.button(
            {
                "class": "py-btn-follow py-btn-following" if seguindo else "py-btn-follow",
                "on_click": toggle_follow_click,
            },
            "Seguindo" if seguindo else "Seguir",
        )

    return html.div(
        {"class": "py-overlay", "on_click": on_close},
        html.div(
            {"class": "py-modal", "on_click": event(lambda e: None, stop_propagation=True)},
            html.button(
                {"class": "py-icon-btn py-modal-close", "on_click": on_close, "title": "Fechar"},
                IconClose(20),
            ),
            html.h3({"class": "py-modal-title"}, "Perfil"),
            html.div(
                {"class": "py-profile-row"},
                html.div(
                    {"class": "py-avatar"},
                    html.img({"src": dados["profile_pic"], "alt": dados["name"]}),
                ),
                html.div(
                    {"class": "py-profile-info"},
                    html.div({"class": "py-profile-name"}, dados["name"]),
                    html.div(
                        {"class": "py-profile-meta"},
                        "Membro desde "
                        + time.strftime("%d/%m/%Y", time.localtime(dados.get("created") or 0)),
                    ),
                ),
                botao_seguir,
            ),
            html.div(
                {"class": "py-stats"},
                html.span({"class": "py-stat"}, html.strong({}, str(stats["posts"])), "posts"),
                html.span(
                    {"class": "py-stat"}, html.strong({}, str(seguidores)), "seguidores"
                ),
                html.span(
                    {"class": "py-stat"}, html.strong({}, str(stats["following"])), "seguindo"
                ),
                html.span({"class": "py-stat"}, html.strong({}, str(stats["views"])), "views"),
            ),
        ),
    )
