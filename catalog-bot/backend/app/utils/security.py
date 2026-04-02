from cryptography.fernet import Fernet
from app.core.config import settings

try:
    cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode('utf-8'))
except Exception:
    # Fallback to ephemeral key for testing if .env has an invalid format
    cipher_suite = Fernet(Fernet.generate_key())

def encrypt_token(plain_token: str) -> str:
    if not plain_token:
        return ""
    return cipher_suite.encrypt(plain_token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    if not encrypted_token:
        return ""
    try:
        return cipher_suite.decrypt(encrypted_token.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return ""
