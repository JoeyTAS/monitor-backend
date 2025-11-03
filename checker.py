import httpx
import time
import datetime
from app.database import supabase 


# La misma lógica de escaneo que tenías antes
def get_site_metrics(url: str) -> dict:
    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            response = client.get(url)
            response_time_ms = int(response.elapsed.total_seconds() * 1000)

            if response.is_success:
                status = "online"
            else:
                status = "offline" 

            return {
                "status": status,
                "response_time": response_time_ms
            }
    except Exception:
        return {
            "status": "offline",
            "response_time": 0
        }

def run_checker():
    """Bucle infinito que chequea todos los sitios."""
    print("Iniciando el chequeador...")
    while True:
        try:
            # 1. Obtener TODOS los sitios de la base de datos
            response = supabase.table("sites").select("id, url").execute()
            sites = response.data
            
            if not sites:
                print("No hay sitios para chequear. Durmiendo...")
            else:
                print(f"Chequeando {len(sites)} sitios...")
            
            for site in sites:
                # 2. Obtener las métricas reales
                metrics = get_site_metrics(site['url'])
                
                # 3. Guardar el resultado en el historial (site_logs)
                log_data = {
                    "site_id": site['id'],
                    "status": metrics['status'],
                    "response_time": metrics['response_time'],
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
                
                supabase.table("site_logs").insert(log_data).execute()
                print(f"  > Log de {site['url']}: {metrics['status']} ({metrics['response_time']}ms)")
                
                # Pequeña pausa para no saturar
                time.sleep(1) 

        except Exception as e:
            print(f"Error en el bucle principal del checker: {e}")
        
        # 4. Dormir antes de la siguiente ronda
        # Chequear "cada segundos" es demasiado agresivo.
        # Pongámoslo cada 60 segundos (1 minuto).
        print("Ciclo completado. Durmiendo por 60 segundos...")
        time.sleep(60)

if __name__ == "__main__":
    run_checker()