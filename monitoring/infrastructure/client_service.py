import requests
import threading
from datetime import datetime

class CloudSaaSGatewayClient:
    """Asynchronous component for unified synchronization to the Cloud Backend.
    
    Takes the total data packet processed at the Edge and sends it in a block
    via HTTP POST to the internet to feed the Nexora Web App and Mobile App.
    """
    def __init__(self):
        # Unified endpoint of the central Cloud Backend
        self.cloud_sync_url = "https://api.nexora-platform.com/v1/cloud-sync/ingest"

    def dispatch_payload_to_cloud_async(self, data: dict):
        """Triggers an independent thread of execution to avoid network latency at the Edge."""
        worker = threading.Thread(target=self._execute_post, args=(data,))
        worker.daemon = True
        worker.start()

    def _execute_post(self, data: dict):
        try:
            # Transparent synchronization via REST API
            response = requests.post(self.cloud_sync_url, json=data, timeout=4)
            if response.status_code == 201:
                print(f"[EDGE-TO-CLOUD SUCCESS] Payload indexed in the cloud for unit {data['apartment_id']}")
        except requests.exceptions.RequestException:
            print("[CLOUD SYNC OFFLINE] Edge disconnected from the cloud. Local resilience active in SQLite.")