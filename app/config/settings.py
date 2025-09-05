from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FRONTEND_ORIGIN: str
    GOOGLE_API_KEY: str
    META_ACCESS_TOKEN: str
    META_PHONE_NUMBER_ID: str
    META_API_VERSION: str
    META_VERIFY_TOKEN: str
    PROMPT_SHEET_ID: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()