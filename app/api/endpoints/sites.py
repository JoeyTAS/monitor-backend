from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from urllib.parse import urlparse
from ...database import supabase
from ...models import SiteCreate, Site, SiteLog
from ..deps import get_current_user_id # Importamos la dependencia

router = APIRouter()

@router.post("/", response_model=Site, status_code=status.HTTP_201_CREATED)
def add_site(
    site: SiteCreate, 
    user_id: str = Depends(get_current_user_id)
):
    """Lógica para crear un sitio (antes en crud.py)"""
    try:
        hostname = urlparse(str(site.url)).hostname or str(site.url)
        name = hostname.replace("www.", "")
    except Exception:
        name = str(site.url)
        
    try:
        res = supabase.table("sites").insert({
            "url": str(site.url), "name": name, "user_id": user_id
        }).execute()

        new_site = res.data[0]
        return Site(id=new_site['id'], url=new_site['url'], name=new_site['name'], latest_log=None)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al añadir el sitio.")

@router.get("/", response_model=List[Site])
def get_user_sites(user_id: str = Depends(get_current_user_id)):
    """Lógica para obtener sitios (antes en crud.py)"""
    try:
        sites_response = supabase.table("sites").select("*").eq("user_id", user_id).execute()
        sites_data = sites_response.data
        if not sites_data: return []

        sites_list = []
        for site in sites_data:
            log_response = supabase.table("site_logs").select("*") \
                               .eq("site_id", site['id']) \
                               .order("timestamp", desc=True) \
                               .limit(1) \
                               .execute()
            latest_log_data = log_response.data[0] if log_response.data else None
            sites_list.append(
                Site(
                    id=site['id'],
                    url=site['url'],
                    name=site['name'],
                    latest_log=SiteLog.model_validate(latest_log_data) if latest_log_data else None
                )
            )
        return sites_list
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error de servidor al obtener los sitios.")

@router.get("/{site_id}/history", response_model=List[SiteLog])
def get_site_history(
    site_id: str, 
    user_id: str = Depends(get_current_user_id)
):
    """Lógica para obtener historial (antes en crud.py)"""
    try:
        site_response = supabase.table("sites").select("id, user_id").eq("id", site_id).single().execute()
        if not site_response.data or site_response.data['user_id'] != user_id:
            raise HTTPException(status_code=404, detail="Sitio no encontrado o no autorizado")

        logs_response = supabase.table("site_logs").select("*") \
                             .eq("site_id", site_id) \
                             .order("timestamp", desc=True) \
                             .limit(100) \
                             .execute()
        return [SiteLog.model_validate(log) for log in logs_response.data]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error de servidor al obtener los logs.")