import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import constant_time
import secrets
import binascii

AES_KEY = bytes.fromhex(os.getenv("AES_SECRET_KEY"))

BLOCK_SIZE = 128  


def encrypt_message(plain_text: str) -> tuple[str, str]:
    """Шифрует сообщение Возвращает (encrypted_text_hex, iv_hex)"""
    
    iv = secrets.token_bytes(16)

    padder = PKCS7(BLOCK_SIZE).padder()
    padded_data = padder.update(plain_text.encode()) + padder.finalize()

    cipher = Cipher(
        algorithms.AES(AES_KEY),
        modes.CBC(iv),
        backend=default_backend()
    )

    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    return (
        binascii.hexlify(encrypted).decode(),
        binascii.hexlify(iv).decode()
    )


def decrypt_message(encrypted_hex: str, iv_hex: str) -> str:
    """Расшифровывает сообщение"""

    encrypted = binascii.unhexlify(encrypted_hex)
    iv = binascii.unhexlify(iv_hex)

    cipher = Cipher(
        algorithms.AES(AES_KEY),
        modes.CBC(iv),
        backend=default_backend()
    )

    decryptor = cipher.decryptor()
    padded_plain = decryptor.update(encrypted) + decryptor.finalize()

    unpadder = PKCS7(BLOCK_SIZE).unpadder()
    plain = unpadder.update(padded_plain) + unpadder.finalize()

    return plain.decode()
