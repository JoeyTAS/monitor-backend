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
            response = supabase.table("sites").select("id, url").execute()
            sites = response.data

            down_sites_to_alert = []  # ← almacenar los sitios caídos del ciclo

            for site in sites:
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

                # Detectar caída online → offline
                previous = LAST_STATUS.get(site_id)
                if previous != "offline" and metrics["status"] == "offline":
                    down_sites_to_alert.append(url)

                LAST_STATUS[site_id] = metrics["status"]
                time.sleep(1)

            # 🔥 SI HAY UNO O VARIOS SITIOS CAÍDOS → SOLO UN CORREO
            if down_sites_to_alert:
                print("⚠ Sitios caídos detectados:", down_sites_to_alert)
                send_alert_email("joeyta3017@gmail.com", down_sites_to_alert)

        except Exception as e:
            print(f"Error en el bucle principal del checker: {e}")

        print("Ciclo completado. Durmiendo por 60 segundos...\n")
        time.sleep(60)


if __name__ == "__main__":
    run_checker()
