"""Ícones SVG inline do Pythomic (sem emojis na interface).

São funções simples (sem hooks) — podem ser chamadas inline como filhos de
outros elementos, sem custo de componente.
"""

from reactpy import svg


def _icon(size, *paths, fill="none", stroke="currentColor", stroke_width=2):
    """Monta um <svg> 24x24 com os caminhos informados (estilo stroke)."""
    return svg.svg(
        {
            "viewBox": "0 0 24 24",
            "width": f"{size}px",
            "height": f"{size}px",
            "fill": fill,
            "stroke": stroke,
            "strokeWidth": stroke_width,
            "strokeLinecap": "round",
            "strokeLinejoin": "round",
            "aria-hidden": "true",
        },
        *[svg.path({"d": d}) for d in paths],
    )


HEART_PATH = (
    "M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78"
    "l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
)
HOME_PATHS = ("M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z", "M9 22V12h6v10")
PLUS_PATHS = ("M12 5v14", "M5 12h14")
MENU_PATHS = ("M3 6h18", "M3 12h18", "M3 18h18")
CLOSE_PATHS = ("M18 6L6 18", "M6 6l12 12")
MOON_PATHS = ("M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z",)
SUN_PATHS = (
    "M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10z",
    "M12 1v2", "M12 21v2", "M4.22 4.22l1.42 1.42", "M18.36 18.36l1.42 1.42",
    "M1 12h2", "M21 12h2", "M4.22 19.78l1.42-1.42", "M18.36 5.64l1.42-1.42",
)
LOGOUT_PATHS = ("M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4", "M16 17l5-5-5-5", "M21 12H9")
REFRESH_PATHS = (
    "M23 4v6h-6", "M1 20v-6h6",
    "M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15",
)
CHECK_PATHS = ("M20 6L9 17l-5-5",)
EYE_PATHS = ("M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z", "M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z")
EYE_OFF_PATHS = (
    "M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94",
    "M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19",
    "M14.12 14.12a3 3 0 1 1-4.24-4.24",
    "M1 1l22 22",
)
SHIELD_PATHS = ("M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",)
LOCK_PATHS = ("M7 11h10v10H7z", "M7 11V7a5 5 0 0 1 10 0v4")
DEVICES_PATHS = ("M2 4h14v10H2z", "M6 18h6", "M9 14v4", "M17 8h4v12h-4z", "M19 17h.01")
IMAGE_PATHS = (
    "M21 19V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2z",
    "M8.5 10a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z",
    "M21 15l-5-5L5 21",
)
CAMERA_PATHS = (
    "M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z",
    "M16 13a4 4 0 1 1-8 0 4 4 0 0 1 8 0z",
)
TRASH_PATHS = (
    "M3 6h18",
    "M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2",
    "M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6",
    "M10 11v6",
    "M14 11v6",
)
MAIL_PATHS = (
    "M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z",
    "M22 6l-10 7L2 6",
)
ARROW_LEFT_PATHS = ("M19 12H5", "M12 19l-7-7 7-7")


def HeartIcon(filled, size=26):
    """Coração do botão curtir: preenchido (vermelho) ou contorno."""
    if filled:
        return _icon(size, HEART_PATH, fill="#ef4458", stroke="none")
    return _icon(size, HEART_PATH)


def IconHome(size=22):
    return _icon(size, *HOME_PATHS)


def IconPlus(size=22):
    return _icon(size, *PLUS_PATHS)


def IconMenu(size=22):
    return _icon(size, *MENU_PATHS)


def IconClose(size=20):
    return _icon(size, *CLOSE_PATHS)


def IconMoon(size=22):
    return _icon(size, *MOON_PATHS)


def IconSun(size=22):
    return _icon(size, *SUN_PATHS)


def IconLogout(size=20):
    return _icon(size, *LOGOUT_PATHS)


def IconRefresh(size=16):
    return _icon(size, *REFRESH_PATHS)


def IconCheck(size=14):
    return _icon(size, *CHECK_PATHS)


def IconEye(size=20):
    return _icon(size, *EYE_PATHS)


def IconEyeOff(size=20):
    return _icon(size, *EYE_OFF_PATHS)


def IconShield(size=20):
    return _icon(size, *SHIELD_PATHS)


def IconLock(size=20):
    return _icon(size, *LOCK_PATHS)


def IconDevices(size=20):
    return _icon(size, *DEVICES_PATHS)


def IconImage(size=48):
    return _icon(size, *IMAGE_PATHS)


def IconCamera(size=20):
    return _icon(size, *CAMERA_PATHS)


def IconTrash(size=20):
    return _icon(size, *TRASH_PATHS)


def IconMail(size=20):
    return _icon(size, *MAIL_PATHS)


def IconArrowLeft(size=20):
    return _icon(size, *ARROW_LEFT_PATHS)
