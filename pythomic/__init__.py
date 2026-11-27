"""Pythomic — rede social estilo Instagram feita em Python (ReactPy + Flask).

Pacote principal. A versão original era um único arquivo (~2300 linhas); agora
o código está separado por responsabilidade para facilitar a manutenção:

    pythomic/
        config.py      # caminhos, constantes, segredo mestre
        security.py    # criptografia de campos, hash de senha, rate limit
        database.py    # schema SQLite + consultas
        uploads.py     # validação de mídia (magic bytes, tamanho, tipo)
        server.py      # app Flask, cabeçalhos de segurança, init
        ui/
            styles.py     # CSS global (mobile-only, moderno, animado)
            scripts.py    # JS injetado (tema, upload base64)
            icons.py      # ícones SVG inline
            components/    # um arquivo por tela ReactPy

Para executar, rode (a partir da pasta do projeto):

    python run.py
"""
__version__ = "2.0.0"
