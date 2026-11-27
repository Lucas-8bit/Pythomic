"""Ponto de entrada do Pythomic.

Rode a partir da pasta do projeto (a pasta que contém este arquivo):

    python run.py

Depois abra no navegador (celular ou emulação mobile do DevTools, pois a
interface é mobile-only):

    http://localhost:5000

Variáveis de ambiente opcionais:
    PYTHOMIC_SECRET  — segredo mestre da criptografia (ver pythomic/config.py)
    PYTHOMIC_DEBUG=1 — liga o modo debug do Flask (apenas em desenvolvimento)
"""

import os

from reactpy import html
from reactpy.backend.flask import Options, configure

from pythomic.server import app
from pythomic.ui.components.app import App

# Cabeçalho <head> customizado. O shell padrão do ReactPy NÃO inclui a
# <meta name="viewport"> — sem ela, navegadores mobile renderizam a página a
# ~980px (escala de desktop), deixando a interface minúscula e "bugada".
# Aqui forçamos width=device-width + initial-scale=1 para a UI ocupar toda a
# tela do celular/tablet, além de theme-color, título e suporte a PWA básico.
HEAD = [
    html.title("Pythomic — Rede Social"),
    html.meta(
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1, maximum-scale=5, "
            "viewport-fit=cover",
        }
    ),
    html.meta(
        {"name": "theme-color", "content": "#5b5bf6",
         "media": "(prefers-color-scheme: light)"}
    ),
    html.meta(
        {"name": "theme-color", "content": "#05060c",
         "media": "(prefers-color-scheme: dark)"}
    ),
    html.meta(
        {"name": "description", "content": "Pythomic — rede social mobile em Python"}
    ),
    html.meta({"name": "apple-mobile-web-app-capable", "content": "yes"}),
    html.meta(
        {"name": "apple-mobile-web-app-status-bar-style", "content": "black-translucent"}
    ),
    html.meta({"name": "mobile-web-app-capable", "content": "yes"}),
    html.link(
        {"rel": "icon", "href": "/_reactpy/assets/reactpy-logo.ico",
         "type": "image/x-icon"}
    ),
]

# Liga a interface ReactPy ao servidor Flask, com o <head> customizado.
configure(app, App, options=Options(head=HEAD))


if __name__ == "__main__":
    # Debug desativado por padrão: o debugger interativo do Werkzeug permite
    # execução remota de código se exposto. Ative apenas em desenvolvimento
    # com a variável de ambiente PYTHOMIC_DEBUG=1.
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("PYTHOMIC_DEBUG") == "1")
