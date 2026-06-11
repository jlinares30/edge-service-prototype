# src/shared/infrastructure/database.py
from peewee import SqliteDatabase

# Instancia única de la base de datos SQLite local del Edge.
# Se creará el archivo 'nexora_edge.db' en la raíz del proyecto.
db = SqliteDatabase('nexora_edge.db')


def init_db() -> None:
    """Abre la conexión y crea las tablas requeridas de forma idempotente.
    
    Realiza importaciones diferidas (at call time) para evitar dependencias circulares
    entre los bounded contexts de IAM y Monitoring.
    """
    db.connect()
    
    # Importaciones diferidas
    from iam.infrastructure.models import Device as DeviceModel
    from monitoring.infrastructure.models import TelemetryRecordModel, PropertyAssetStateModel
    
    # Crea las tablas si no existen en el archivo SQLite
    db.create_tables([DeviceModel, TelemetryRecordModel, PropertyAssetStateModel], safe=True)
    db.close()