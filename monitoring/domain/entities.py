from datetime import datetime
from typing import Dict, Any

class PropertyAsset:
    """Aggregate Root que representa el núcleo de control IoT de una vivienda en el Edge.
    
    Gestiona los estados de los actuadores, la configuración de seguridad perimetral
    y centraliza las lecturas multivariables (Gas, Agua, Luz, Puertas).
    """

    def __init__(
        self, 
        device_id: str, 
        apartment_id: str, 
        is_security_mode_armed: bool = False,
        is_valve_closed: bool = False,
        is_door_locked: bool = True,
        id: int = None
    ):
        self.id = id
        self.device_id = device_id
        self.apartment_id = apartment_id
        self.is_security_mode_armed = is_security_mode_armed
        self.is_valve_closed = is_valve_closed
        self.is_door_locked = is_door_locked
        
        # Estado analítico local para el control de desperdicios de agua
        self.water_flow_start_time = None

    def process_telemetry(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica las reglas e invariantes del Dominio basándose en la carga útil IoT.
        
        Retorna las acciones tácticas inmediatas (comandos de actuación) y el nivel
        de criticidad del evento para su escalamiento.
        """
        gas_ppm = float(raw_data.get("gas_ppm", 0.0))
        water_flow = float(raw_data.get("water_flow", 0.0)) # en litros/min
        is_smoke_detected = bool(raw_data.get("smoke_detected", False))
        is_motion_detected = bool(raw_data.get("motion_detected", False))
        is_door_open = bool(raw_data.get("door_open", False))

        actions = {"valve_command": "KEEP_OPEN", "door_command": "KEEP_STATE"}
        severity = "OK"
        alert_type = None
        message = "System operational"

        # 1. INVARIANTE: Incidencias Críticas (Máxima prioridad - Nivel Rojo)
        if gas_ppm >= 400.0 or is_smoke_detected:
            self.is_valve_closed = True
            actions["valve_command"] = "CLOSE"
            severity = "CRITICAL_INCIDENT"
            alert_type = "FIRE_GAS_EMERGENCY"
            message = "Alta concentración de riesgo inflamable/humo detectada. Válvula clausurada."
            return {"severity": severity, "alert_type": alert_type, "message": message, "actions": actions}

        if self.is_security_mode_armed and (is_motion_detected or is_door_open):
            severity = "CRITICAL_INCIDENT"
            alert_type = "INTRUSION_DETECTED"
            message = "Intrusión detectada perimetralmente en propiedad desocupada bajo Modo Seguridad."
            return {"severity": severity, "alert_type": alert_type, "message": message, "actions": actions}

        # 2. INVARIANTE: Alertas de Prevención (Eficiencia y control menor - Nivel Amarillo)
        if gas_ppm > 50.0 and gas_ppm < 400.0:
            severity = "PREVENTION"
            alert_type = "MICRO_LEAK_GAS"
            message = "Variación anómala menor detectada en los sensores de gas de la cocina."
            
        elif water_flow > 0.0:
            # Control lógico local de fuga/desperdicio de agua (ej. grifo abierto > 15 mins)
            if not self.water_flow_start_time:
                self.water_flow_start_time = datetime.utcnow()
            else:
                elapsed_minutes = (datetime.utcnow() - self.water_flow_start_time).total_seconds() / 60.0
                if elapsed_minutes >= 15.0:
                    severity = "PREVENTION"
                    alert_type = "WATER_WASTE_ALERT"
                    message = "Flujo continuo de agua detectado por más de 15 minutos en la unidad."
        else:
            self.water_flow_start_time = None # Reseteo de flujo de agua

        return {
            "severity": severity,
            "alert_type": alert_type,
            "message": message,
            "actions": actions
        }

    def change_security_mode(self, arm: bool):
        """Habilita o deshabilita el Modo Seguridad para propiedades desocupadas."""
        self.is_security_mode_armed = arm

    def execute_remote_lock(self, lock: bool):
        """Modifica el estado de la cerradura inteligente (Gestión Inmediata de Acceso)."""
        self.is_door_locked = lock