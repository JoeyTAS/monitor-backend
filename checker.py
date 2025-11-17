import httpx
import time
import datetime
from app.database import supabase
from app.email_utils import send_alert_email

LAST_STATUS = {}

def get_site_metrics(url: str) -> dict:
    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            response = client.get(url)
            response_time_ms = int(response.elapsed.total_seconds() * 1000)
            status = "online" if response.is_success else "offline"
            return {"status": status, "response_time": response_time_ms}
    except Exception:
        return {"status": "offline", "response_time": 0}


def run_checker():
    print("Iniciando el chequeador...")

    while True:
        try:
            # Obtener todos los sitios
            sites_res = supabase.table("sites").select("id, url, user_id").execute()
            sites = sites_res.data
            if not sites:
                print("No hay sitios registrados.")
                time.sleep(60)
                continue

            # Obtener todos los usuarios
            users_list = supabase.auth.admin.list_users()  # Devuelve objetos User
            emails_mapping = {u.id: u.email for u in users_list if hasattr(u, "email") and u.email}

            # Filtrar solo usuarios con sitios
            user_sites = {}
            for site in sites:
                user_id = site.get("user_id")
                if user_id and user_id in emails_mapping:
                    user_sites.setdefault(user_id, []).append(site)

            down_sites_per_user = {}

            # Revisar sitios y registrar caídas
            for user_id, sites_list in user_sites.items():
                for site in sites_list:
                    site_id = site["id"]
                    url = site["url"]

                    metrics = get_site_metrics(url)

                    # Guardar log
                    supabase.table("site_logs").insert({
                        "site_id": site_id,
                        "status": metrics["status"],
                        "response_time": metrics["response_time"],
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }).execute()

                    previous = LAST_STATUS.get(site_id)
                    if previous != "offline" and metrics["status"] == "offline":
                        down_sites_per_user.setdefault(user_id, []).append(url)

                    LAST_STATUS[site_id] = metrics["status"]
                    time.sleep(1)

            # Enviar alertas solo a usuarios con sitios caídos
            for user_id, urls in down_sites_per_user.items():
                email = emails_mapping.get(user_id)
                if email:
                    print(f"Enviando alerta a {email} por sitios caídos: {urls}")
                    send_alert_email(email, urls)

        except Exception as e:
            print(f"Error en el bucle principal del checker: {e}")

        print("Ciclo completado. Durmiendo por 60 segundos...\n")
        time.sleep(60)


if __name__ == "__main__":
    run_checker()
