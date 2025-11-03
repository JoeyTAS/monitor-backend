from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import datetime

# --- Modelos de Autenticación ---
# (Esto es lo que falta y causa el error)

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Modelos de Sitios ---

class SiteBase(BaseModel):
    url: HttpUrl # pydantic valida que sea una URL

class SiteCreate(SiteBase):
    pass

class SiteLog(BaseModel):
    # Esto es lo que devuelve el historial
    id: int
    site_id: str
    timestamp: datetime.datetime
    status: str
    response_time: int
    
    class Config:
        # Esto permite que Pydantic lea datos
        # directamente de un objeto de base de datos
        from_attributes = True 

class Site(BaseModel):
    # Esto es lo que devuelve la lista de sitios
    id: str
    url: HttpUrl
    name: str
    # 'latest_log' contendrá el último estado conocido
    latest_log: Optional[SiteLog] = None

    class Config:
        from_attributes = True