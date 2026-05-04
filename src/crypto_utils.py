"""Utilidades criptográficas: hashing SHA-256 y generación de identificadores."""

import hashlib
import json
import uuid


def hash_data(data: str) -> str:
    """Genera un hash SHA-256 de una cadena de texto."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def generate_id() -> str:
    """Genera un identificador único de 8 caracteres basado en UUID4."""
    return str(uuid.uuid4())[:8]


def hash_block(
    index: int,
    timestamp: str,
    data: dict,
    previous_hash: str,
    nonce: int,
) -> str:
    """Genera el hash SHA-256 de un bloque a partir de sus campos."""
    block_string = json.dumps(
        {
            "index": index,
            "timestamp": timestamp,
            "data": data,
            "previous_hash": previous_hash,
            "nonce": nonce,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hash_data(block_string)
