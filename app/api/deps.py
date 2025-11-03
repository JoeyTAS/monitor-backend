from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..database import supabase # .. significa "subir un nivel"

# La URL del token ahora es más específica
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """Valida el token y devuelve el ID del usuario."""
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
        return user.id
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")