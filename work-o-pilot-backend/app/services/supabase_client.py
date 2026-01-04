from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client | None:
    url: str = settings.SUPABASE_URL
    key: str = settings.SUPABASE_KEY
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        return None

supabase: Client | None = get_supabase_client()
