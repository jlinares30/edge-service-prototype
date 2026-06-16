from peewee import Model, AutoField, CharField, FloatField, BooleanField, DateTimeField
from shared.infrastructure.database import db

class TelemetryRecordModel(Model):
    """Saves the raw historical log of consolidated telemetry at the edge."""
    id = AutoField()
    device_id = CharField()
    gas_ppm = FloatField()
    water_flow = FloatField()
    electricity_kwh = FloatField()
    water_m3 = FloatField()
    severity = CharField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'telemetry_records'

class PropertyAssetStateModel(Model):
    """Maps the current state of the Domain Aggregate to persist actuators and modes."""
    device_id = CharField(primary_key=True)
    apartment_id = CharField()
    is_security_mode_armed = BooleanField(default=False)
    is_valve_closed = BooleanField(default=False)
    is_door_locked = BooleanField(default=True)

    class Meta:
        database = db
        table_name = 'property_assets_state'