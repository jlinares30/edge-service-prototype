from datetime import datetime
from monitoring.domain.repositories import IPropertyAssetRepository
from monitoring.infrastructure.models import GasRecordModel
from monitoring.infrastructure.client_service import CloudSaaSGatewayClient

class TelemetryApplicationService:
    """Orquestador de Casos de Uso del ecosistema IoT unificado de Nexora."""

    def __init__(self, repository: IPropertyAssetRepository):
        self.repository = repository
        self.cloud_client = CloudSaaSGatewayClient()

    def handle_incoming_telemetry(self, device_id: str, payload: dict) -> dict:
        # 1. Recuperar o inicializar de forma segura el Agregado del Dominio en el Borde
        asset = self.repository.find_by_device_id(device_id)
        if not asset:
            from monitoring.domain.entities import PropertyAsset
            asset = PropertyAsset(device_id=device_id, apartment_id=payload.get("apartment_id", "Apt-Unknown"))

        # 2. Ejecución de lógica de negocio pura del dominio (Invariantes de alertas)
        evaluation = asset.process_telemetry(payload)

        # 3. Guardar el estado de los actuadores del Agregado
        self.repository.save(asset)

        # 4. Registrar logs históricos locales para la auditoría y consumos ($m^3$, kWh)
        GasRecordModel.create(
            device_id=device_id,
            gas_ppm=float(payload.get("gas_ppm", 0.0)),
            water_flow=float(payload.get("water_flow", 0.0)),
            electricity_kwh=float(payload.get("electricity_kwh", 0.0)),
            water_m3=float(payload.get("water_m3", 0.0)),
            severity=evaluation["severity"],
            created_at=datetime.utcnow()
        )

        # 5. CONSOLIDACIÓN: Preparar el payload unificado total que requiere el Backend Cloud
        cloud_payload = {
            "device_id": device_id,
            "apartment_id": asset.apartment_id,
            "telemetry": payload,
            "system_state": {
                "is_security_mode_armed": asset.is_security_mode_armed,
                "is_valve_closed": asset.is_valve_closed,
                "is_door_locked": asset.is_door_locked
            },
            "evaluation": {
                "severity": evaluation["severity"],
                "alert_type": evaluation["alert_type"],
                "message": evaluation["message"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Despacho asíncrono
        self.cloud_client.dispatch_payload_to_cloud_async(cloud_payload)

        # Retornar directivas de acción física inmediata en la respuesta HTTP hacia el Embedded App
        return {
            "status": "PROCESSED",
            "valve_status": "CLOSED" if asset.is_valve_closed else "OPEN",
            "door_status": "LOCKED" if asset.is_door_locked else "UNLOCKED",
            "actions": evaluation["actions"]
        }

    def remote_toggle_security_mode(self, device_id: str, arm: bool) -> bool:
        """Caso de Uso disparado desde la nube para cambiar el Modo Seguridad."""
        asset = self.repository.find_by_device_id(device_id)
        if asset:
            asset.change_security_mode(arm)
            self.repository.save(asset)
            return True
        return False