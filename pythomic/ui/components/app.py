"""Componente raiz (App): roteamento simples, tema persistente e CSS global."""

from reactpy import component, html, use_state

from ..scripts import THEME_BOOT_SCRIPT, _theme_sync_script
from ..styles import GLOBAL_CSS
from .auth import AuthScreen
from .home import HomeScreen
from .welcome import WelcomeScreen


@component
def App():
    """Raiz da aplicação: roteamento simples, tema persistente e CSS global."""
    page, set_page = use_state("welcome")
    user, set_user = use_state(None)
    is_dark, set_is_dark = use_state(False)
    theme_ready, set_theme_ready = use_state(False)

    def handle_theme_input(e):
        """Recebe do script de boot o tema salvo no navegador (padrão hidden-input)."""
        valor = e["target"]["value"]
        set_is_dark(valor == "dark")
        set_theme_ready(True)  # libera o script de sincronização após o boot

    if page == "home" and user:
        tela = HomeScreen(user, set_user, is_dark, set_is_dark)
    elif page == "auth":
        tela = AuthScreen(set_page, set_user)
    else:
        tela = WelcomeScreen(set_page)

    return html.div(
        {"class": "py-shell"},
        html.style(GLOBAL_CSS),
        html.input(
            {"type": "hidden", "id": "py_theme_input", "on_change": handle_theme_input}
        ),
        # Boot: aplica o tema salvo no localStorage (roda uma vez na montagem).
        html.script({"key": "py-theme-boot"}, THEME_BOOT_SCRIPT),
        # Sincronização: só entra em cena depois do boot, para não sobrescrever
        # o tema persistido; a key muda a cada alternância e re-executa o script.
        html.script(
            {"key": f"py-theme-sync-{is_dark}"}, _theme_sync_script(is_dark)
        ) if theme_ready else None,
        tela,
    )
