"""Uploads validados do Pythomic.

A mídia chega ao servidor como data URL (base64) por meio de um input
escondido (padrão do projeto). Aqui validamos:
    * tamanho máximo (10 MB);
    * tipo REAL do arquivo pelos magic bytes (assinatura), não pelo tipo
      declarado pelo navegador — para barrar arquivos disfarçados;
    * whitelist de MIME (JPEG, PNG, GIF, WEBP, MP4);
    * decodificação base64 estrita.

O arquivo é salvo com nome aleatório (uuid4) em UPLOAD_DIR e devolvido como
caminho público "/uploads/<arquivo>".
"""

import base64
import os
import uuid

from .config import MAX_FILE_SIZE, UPLOAD_DIR


class UploadError(Exception):
    """Erro de validação de upload com mensagem amigável em pt-BR."""


# Tipos permitidos e suas extensões (whitelist MIME)
ALLOWED_MIME = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
}


def _magic_mime(data: bytes):
    """Identifica o tipo REAL do arquivo pelos magic bytes (assinatura).

    JPEG: FF D8 FF | PNG: 89 50 4E 47 | GIF: "GIF8"
    WEBP: "RIFF" nos bytes 0-4 e "WEBP" nos bytes 8-12
    MP4:  "ftyp" nos bytes 4-8
    """
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:4] == b"\x89\x50\x4e\x47":
        return "image/png"
    if data[:4] == b"GIF8":
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data[4:8] == b"ftyp":
        return "video/mp4"
    return None


def save_media(base64_data, filename_prefix, images_only=False) -> str:
    """Valida e grava a mídia enviada (data URL em base64).

    Validações: tipo declarado x magic bytes, tamanho máximo (10 MB) e
    decodificação base64 estrita. O arquivo é salvo com nome aleatório
    (uuid4) para evitar colisões e caminhos previsíveis.
    Com images_only=True (foto de perfil), vídeos são rejeitados.
    Retorna o caminho público "/uploads/<arquivo>".
    """
    if not base64_data:
        raise UploadError("Nenhum arquivo recebido.")

    header, encoded = "", base64_data
    if "," in base64_data:
        header, encoded = base64_data.split(",", 1)
    declarado = ""
    if header.startswith("data:"):
        declarado = header[5:].split(";", 1)[0].lower()

    try:
        data = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError):
        raise UploadError("Arquivo corrompido ou inválido.")

    if not data:
        raise UploadError("Arquivo vazio.")
    if len(data) > MAX_FILE_SIZE:
        raise UploadError("Arquivo muito grande (máximo: 10 MB).")

    real = _magic_mime(data)
    if real is None:
        raise UploadError("Tipo de arquivo não permitido (use JPG, PNG, GIF, WEBP ou MP4).")
    if images_only and not real.startswith("image/"):
        raise UploadError("A foto de perfil deve ser uma imagem (JPG, PNG, GIF ou WEBP).")
    if declarado and declarado != real:
        # O navegador declarou um tipo, mas a assinatura do arquivo é outra:
        # indício clássico de arquivo disfarçado — rejeite.
        raise UploadError("O conteúdo do arquivo não corresponde ao tipo declarado.")

    ext = ALLOWED_MIME[real]
    filename = f"{filename_prefix}_{uuid.uuid4().hex}{ext}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(data)
    return f"/uploads/{filename}"


def delete_media(media_path) -> None:
    """Apaga do disco a mídia de um post excluído.

    Só atua em caminhos públicos '/uploads/<nome>' válidos. Usa os.path.basename
    para impedir path traversal (um caminho malicioso '/uploads/../../etc/x'
    vira só o nome do arquivo). Falhas de remoção são silenciadas: o post já
    foi excluído do banco; um arquivo órfão no disco é incômodo menor que
    quebrar a exclusão do post.
    """
    if not media_path or not media_path.startswith("/uploads/"):
        return
    nome = os.path.basename(media_path.split("/uploads/", 1)[1])
    if not nome:
        return
    caminho = os.path.join(UPLOAD_DIR, nome)
    try:
        if os.path.isfile(caminho):
            os.remove(caminho)
    except OSError:
        pass
