"""Aplicação Flask do Pythomic.

A pasta de uploads é servida estaticamente pelo Flask. Cabeçalhos de
segurança são aplicados a TODAS as respostas. O schema do banco e a pasta
de uploads são garantidos no momento da importação (antes de servir qualquer
rota).
"""

import os

from flask import Flask

from .config import MAX_CONTENT_LENGTH, UPLOAD_DIR
from .database import init_db

# A pasta de uploads continua sendo servida estaticamente pelo Flask.
app = Flask(__name__, static_folder=UPLOAD_DIR, static_url_path="/uploads")

# Endurecimento básico do Flask.
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH  # rejeita corpos > 12 MB
app.config["SESSION_COOKIE_HTTPONLY"] = True           # JS não lê cookies
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"          # mitiga CSRF básico


@app.after_request
def _add_security_headers(response):
    """Cabeçalhos de segurança aplicados a TODAS as respostas."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


# Garante schema do banco e pasta de uploads antes de servir qualquer rota.
init_db()
os.makedirs(UPLOAD_DIR, exist_ok=True)
