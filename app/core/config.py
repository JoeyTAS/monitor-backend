import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

class Settings(BaseSettings):
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")

# Instancia única de la configuración
settings = Settings()