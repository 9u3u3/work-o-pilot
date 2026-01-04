from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    GROQ_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX: str = "asset-rag"
    
    # Hardcoded user for now
    DEFAULT_USER_ID: str = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
