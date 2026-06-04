from flask import Blueprint, request, jsonify
from monitoring.application.services import TelemetryApplicationService
from monitoring.infrastructure.repositories import PeeweePropertyAssetRepository
from iam.interfaces.services import authenticate_request

monitoring_api = Blueprint("monitoring_api", __name__)

# Instanciación del servicio de aplicación con su inyección de dependencias
asset_repository = PeeweePropertyAssetRepository()
telemetry_service = TelemetryApplicationService(asset_repository)

@monitoring_api.route("/api/v1/monitoring/telemetry", methods=["POST"])
def ingest_iot_telemetry():
    """Endpoint unificado donde las ESP32 inyectan la telemetría de la vivienda.
    
    Requiere obligatoriamente pasar el guard de autenticación cruzada de IAM
    utilizando el header 'X-API-Key'.
    """
    # Guard del contexto cruzado (IAM)
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.json
    if not data or "device_id" not in data:
        return jsonify({"error": "Payload incompleto o malformado"}), 400

    try:
        device_id = data["device_id"]
        # Procesamiento unificado
        response_data = telemetry_service.handle_telemetry(device_id, data)
        return jsonify(response_data), 200

    except ValueError as val_err:
        return jsonify({"error": str(val_err)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno en el procesamiento del borde"}), 500

@monitoring_api.route("/api/v1/monitoring/security-mode", methods=["PUT"])
def update_security_mode():
    """Endpoint expuesto para que el Backend Cloud configure el Modo Seguridad del inmueble."""
    data = request.json
    if not data or "device_id" not in data or "arm" not in data:
        return jsonify({"error": "Missing parameters"}), 400
        
    success = telemetry_service.remote_toggle_security_mode(data["device_id"], bool(data["arm"]))
    if success:
        return jsonify({"status": "Security mode updated successfully"}), 200
    return jsonify({"error": "Property device not found"}), 404