from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ...database import supabase # ... significa "subir dos niveles"
from ...models import UserCreate, Token

# APIRouter nos permite dividir la app en "mini-apps"
router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    """Lógica de registro (antes en auth.py)"""
    try:
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
        })
        return {"message": "Usuario registrado. Revisa tu email para confirmar.", "user": auth_response.user.email}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Lógica de login (antes en auth.py)"""
    try:
        session = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password,
        })
        return Token(access_token=session.session.access_token, token_type="bearer")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- Obtener usuarios registrados ---
@router.get("/users", status_code=200)
def get_registered_users():
    """
    Devuelve todos los usuarios con email registrado.
    Útil para enviar alertas solo a usuarios con sitios.
    """
    try:
        users_list = supabase.auth.admin.list_users()
        emails = [u["email"] for u in users_list if u.get("email")]
        return {"users": emails}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo usuarios: {str(e)}"
        )



@router.get("/users-with-sites", status_code=200)
def get_users_with_sites():
    """
    Devuelve solo los emails de usuarios que tienen al menos un sitio registrado.
    """
    try:
        # Obtener todos los sitios
        sites_res = supabase.table("sites").select("user_id").execute()
        sites = sites_res.data
        if not sites:
            return {"users": []}

        user_ids = list({s["user_id"] for s in sites if s.get("user_id")})

        # Obtener emails de esos usuarios
        users_list = supabase.auth.admin.list_users()
        emails = [u["email"] for u in users_list if u.get("id") in user_ids and u.get("email")]

        return {"users": emails}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo usuarios con sitios: {str(e)}"
        )