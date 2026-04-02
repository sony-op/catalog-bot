from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    WHATSAPP_TOKEN: str = "dummy_token"
    WHATSAPP_PHONE_NUMBER_ID: str = "dummy_phone_id"
    WHATSAPP_VERIFY_TOKEN: str = "my_verify_token"
    GEMINI_API_KEY: str = "dummy_gemini_key"
    
    # Defaults tailored for basic local testing if no env file exists
    DATABASE_URL: str = "postgresql://user:password@localhost/db"
    ENCRYPTION_KEY: str = "dummy_base64_fernet_key_required_32_bytes="

    class Config:
        env_file = ".env"

settings = Settings()
