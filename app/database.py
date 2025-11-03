from supabase import create_client, Client
from .core.config import settings # Importa la config

# El punto (.) al inicio significa "importar desde el mismo directorio"

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)