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
    
@router.get("/logs/incidents")
def get_incidents(user_id: str = Depends(get_current_user_id)):
    """
    Retorna todas las incidencias (offline) de todos los sitios del usuario.
    Incluye: nombre, url, estado, timestamp y si se envió correo.
    """
    try:
        # 1. Obtener todos los sitios del usuario
        sites_res = supabase.table("sites") \
            .select("id, name, url") \
            .eq("user_id", user_id) \
            .execute()

        sites = sites_res.data
        if not sites:
            return []

        site_ids = [s["id"] for s in sites]

        # 2. Obtener todos los logs offline de esos sitios
        logs_res = supabase.table("site_logs") \
            .select("*") \
            .in_("site_id", site_ids) \
            .eq("status", "offline") \
            .order("timestamp", desc=True) \
            .execute()

        logs = logs_res.data

        # 3. Combinar con datos del sitio
        site_map = {s["id"]: s for s in sites}

        incidents = []
        for log in logs:
            site = site_map.get(log["site_id"])
            if site:
                incidents.append({
                    "id": log["id"],
                    "site_name": site["name"],
                    "url": site["url"],
                    "status": log["status"],
                    "timestamp": log["timestamp"],
                    "email_sent": log.get("email_sent", False)
                })

        return incidents

    except Exception as e:
        print("ERROR INCIDENTS:", e)
        raise HTTPException(status_code=500, detail="Error al obtener las incidencias")
@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(site_id: str, user_id: str = Depends(get_current_user_id)):
    """Eliminar un sitio del usuario"""
    try:
        # Verificar si el sitio existe y pertenece al usuario
        site_response = supabase.table("sites").select("id, user_id").eq("id", site_id).single().execute()
        site = site_response.data
        if not site:
            raise HTTPException(status_code=404, detail="Sitio no encontrado")
        if site["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="No autorizado para eliminar este sitio")
        
        # Eliminar el sitio
        supabase.table("sites").delete().eq("id", site_id).execute()

        return  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        print("ERROR DELETE SITE:", e)
        raise HTTPException(status_code=500, detail="Error de servidor al eliminar el sitio")

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
    

