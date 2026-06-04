import requests
import threading
from datetime import datetime

class CloudSaaSGatewayClient:
    """Componente asíncrono de sincronización unificada hacia el Backend Cloud.
    
    Toma el paquete de datos total procesado en el Edge y lo envía en bloque 
    por HTTP POST a internet para alimentar la Web App y Mobile App de Nexora.
    """
    def __init__(self):
        # Endpoint unificado del Backend central en la nube
        self.cloud_sync_url = "https://api.nexora-platform.com/v1/cloud-sync/ingest"

    def dispatch_payload_to_cloud_async(self, data: dict):
        """Gatilla un hilo de ejecución independiente para evitar latencia de red en el Edge."""
        worker = threading.Thread(target=self._execute_post, args=(data,))
        worker.daemon = True
        worker.start()

    def _execute_post(self, data: dict):
        try:
            # Sincronización transparente vía REST API
            response = requests.post(self.cloud_sync_url, json=data, timeout=4)
            if response.status_code == 201:
                print(f"[EDGE-TO-CLOUD SUCCESS] Payload indexado en la nube para unidad {data['apartment_id']}")
        except requests.exceptions.RequestException:
            print("[CLOUD SYNC OFFLINE] Borde incomunicado con la nube. Resiliencia local activa en SQLite.")