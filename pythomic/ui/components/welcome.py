"""Tela de boas-vindas (hero com logo em gradiente animado)."""

from reactpy import component, html

from ..icons import IconDevices, IconLock, IconShield


@component
def WelcomeScreen(set_page):
    """Tela inicial: hero com logo em gradiente, CTA e diferenciais de segurança."""
    return html.div(
        {"class": "py-welcome"},
        html.h1({"class": "py-logo py-hero-logo"}, "Pythomic"),
        html.p({"class": "py-tagline"}, "Conecte-se com o mundo Python."),
        html.button(
            {"class": "py-btn py-btn-primary py-cta", "on_click": lambda e: set_page("auth")},
            "Começar",
        ),
        html.div(
            {"class": "py-features"},
            html.div(
                {"class": "py-feature"},
                IconShield(20),
                html.span({}, "Criptografia de dados no servidor"),
            ),
            html.div(
                {"class": "py-feature"},
                IconLock(20),
                html.span({}, "Senhas protegidas com PBKDF2"),
            ),
            html.div(
                {"class": "py-feature"},
                IconDevices(20),
                html.span({}, "Interface mobile adaptativa"),
            ),
        ),
    )
