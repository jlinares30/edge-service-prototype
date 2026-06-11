from flask import Flask
from monitoring.interfaces.services import monitoring_api
from iam.interfaces.services import iam_api
from shared.infrastructure.database import db

app = Flask(__name__)
app.register_blueprint(iam_api)
app.register_blueprint(monitoring_api)

first_run = True

@app.before_request
def setup_edge_services():
    global first_run
    if first_run:
        first_run = False
        db.connect()
        from iam.infrastructure.models import Device as DeviceModel
        from monitoring.infrastructure.models import TelemetryRecordModel, PropertyAssetStateModel
        
        # Inicialización segura e idempotente en SQLite local
        db.create_tables([DeviceModel, TelemetryRecordModel, PropertyAssetStateModel], safe=True)
        
        # Sembrar el dispositivo de pruebas del IAM
        from iam.application.services import AuthApplicationService
        auth_service = AuthApplicationService()
        auth_service.get_or_create_test_device()
        
        # db.close() es eliminado aquí para que la conexión siga abierta

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)