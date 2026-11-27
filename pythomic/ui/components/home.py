"""Tela principal (Home): feed + cabeçalho.

Todos os botões de ação ficam no cabeçalho: criar post (+), atualizar, tema e
menu. A barra inferior foi removida — o Atualizar voltou para o topo, ao lado
do +. Modais abrem como top-sheet (descem do topo, coerente com os botões do
cabeçalho).
"""

from reactpy import component, html, use_state

from ...database import get_all_posts, get_user_stats
from ..icons import IconImage, IconMenu, IconMoon, IconPlus, IconRefresh, IconSun
from .create_post import CreatePostModal
from .menu import MenuModal
from .post_card import PostCard
from .profile import ProfileModal


@component
def HomeScreen(user, set_user, is_dark, set_is_dark):
    """Feed + cabeçalho com criar post, atualizar, tema e menu."""
    is_menu_open, set_menu_open = use_state(False)
    is_create_open, set_create_open = use_state(False)
    profile_id, set_profile_id = use_state(None)
    posts, set_posts = use_state(get_all_posts(user["id"]))
    feed_version, set_feed_version = use_state(0)
    stats = get_user_stats(user["id"])

    def refresh_posts():
        set_posts(get_all_posts(user["id"]))
        set_feed_version(lambda v: v + 1)  # ressincroniza curtidas nos cards

    def open_profile(user_id):
        set_profile_id(user_id)

    def toggle_theme(e):
        set_is_dark(not is_dark)

    cabecalho = html.header(
        {"class": "py-header"},
        html.div({"class": "py-logo py-header-logo"}, "Pythomic"),
        html.div(
            {"style": {"display": "flex", "gap": "2px"}},
            html.button(
                {
                    "class": "py-icon-btn",
                    "on_click": lambda e: set_create_open(True),
                    "title": "Criar post",
                    "aria-label": "Criar post",
                },
                IconPlus(22),
            ),
            html.button(
                {
                    "class": "py-icon-btn",
                    "on_click": lambda e: refresh_posts(),
                    "title": "Atualizar página",
                    "aria-label": "Atualizar",
                },
                IconRefresh(22),
            ),
            html.button(
                {
                    "class": "py-icon-btn",
                    "on_click": toggle_theme,
                    "title": "Alternar tema claro/escuro",
                },
                IconMoon(22) if not is_dark else IconSun(22),
            ),
            html.button(
                {
                    "class": "py-icon-btn", "on_click": lambda e: set_menu_open(True),
                    "title": "Abrir menu",
                },
                IconMenu(22),
            ),
        ),
    )

    return html.div(
        {"class": "py-shell"},
        cabecalho,
        html.main(
            {"class": "py-main"},
            html.div(
                {"class": "py-empty"},
                IconImage(48),
                html.p(
                    {"style": {"margin": "0", "fontWeight": "bold", "color": "var(--text)"}},
                    "Seu feed está vazio",
                ),
                html.p(
                    {"style": {"margin": "0", "fontSize": "13px"}},
                    "Siga novas pessoas ou crie o primeiro post pelo ícone + no topo.",
                ),
            ) if not posts else None,
            *[PostCard(p, user, refresh_posts, feed_version, open_profile) for p in posts],
        ),
        CreatePostModal(user, lambda e: set_create_open(False), refresh_posts)
        if is_create_open else None,
        MenuModal(user, set_user, is_dark, set_is_dark,
                  lambda e: set_menu_open(False), refresh_posts)
        if is_menu_open else None,
        ProfileModal(user, profile_id, lambda e: set_profile_id(None), refresh_posts)
        if profile_id else None,
    )
