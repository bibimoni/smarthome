import logging
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from app.extensions import db
from app.models.device import Actuator
from app.models.data import EventLog
from app.services.device_service import DeviceService

logger = logging.getLogger(__name__)


SERVO_COMMAND_COOLDOWN_SECONDS = 15


def get_mqtt_service():
    """Get the MQTT service instance dynamically."""
    from app.services.mqtt_service import mqtt_service
    return mqtt_service


class ActuatorService:
    """Service class for actuator operations."""

    @staticmethod
    def get_all_actuators() -> List[Actuator]:
        return Actuator.query.filter_by(is_active=True).all()

    @staticmethod
    def get_actuator_by_id(actuator_id: int) -> Optional[Actuator]:
        return Actuator.query.get(actuator_id)

    @staticmethod
    def get_actuator_by_feed_key(feed_key: str) -> Optional[Actuator]:
        return Actuator.query.filter_by(feed_key=feed_key).first()

    @staticmethod
    def get_actuators_by_type(actuator_type: str) -> List[Actuator]:
        return Actuator.query.filter_by(type=actuator_type, is_active=True).all()

    @staticmethod
    def _get_latest_manual_log(actuator_id: int) -> Optional[EventLog]:
        return EventLog.query.filter(
            EventLog.actuator_id == actuator_id,
            EventLog.event_type == EventLog.TYPE_MANUAL,
        ).order_by(EventLog.created_at.desc()).first()

    @staticmethod
    def _check_safety_rule(actuator: Actuator, action: str) -> Tuple[bool, str]:
        """
        UC-3 safety rule:
        - Servo không cho nhận lệnh liên tiếp quá nhanh.
        """
        if actuator.type != Actuator.TYPE_SERVO:
            return True, ""

        latest_log = ActuatorService._get_latest_manual_log(actuator.id)
        if not latest_log:
            return True, ""

        metadata = latest_log.event_metadata or {}
        latest_action = metadata.get('action')
        latest_time = latest_log.created_at

        if not latest_time:
            return True, ""

        cooldown_until = latest_time + timedelta(seconds=SERVO_COMMAND_COOLDOWN_SECONDS)
        now = datetime.utcnow()

        if latest_action and latest_action != action and now < cooldown_until:
            wait_seconds = max(1, int((cooldown_until - now).total_seconds()))
            return False, f"Lệnh bị chặn bởi safety rule. Vui lòng thử lại sau {wait_seconds} giây."

        return True, ""

    @staticmethod
    def control_actuator(
        actuator_id: int,
        action: str,
        user_id: int = None,
        manual_override: bool = True,
        auto_switch_to_manual: bool = False,
    ) -> Tuple[bool, str, Optional[dict]]:
        """Control an actuator and return detailed result."""
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found", None

        if not actuator.is_active:
            return False, "Actuator is not active", None

        action = str(action).upper().strip()
        previous_mode = actuator.mode
        previous_value = actuator.current_value

        if actuator.mode == Actuator.MODE_AUTO and manual_override and not auto_switch_to_manual:
            return False, "Thiết bị đang ở AUTO. Hãy chuyển sang MANUAL trước khi điều khiển thủ công.", None

        if actuator.mode == Actuator.MODE_AUTO and manual_override and auto_switch_to_manual:
            actuator.mode = Actuator.MODE_MANUAL

        safe, safe_error = ActuatorService._check_safety_rule(actuator, action)
        if not safe:
            EventLog.log_event(
                event_type=EventLog.TYPE_ERROR,
                description=f"Command blocked by safety rule: {actuator.name} -> {action}",
                actuator_id=actuator.id,
                user_id=user_id,
                device_name=actuator.name,
                metadata={
                    'action': action,
                    'previous_mode': previous_mode,
                    'previous_value': previous_value,
                    'blocked_reason': safe_error,
                },
            )
            return False, safe_error, None

        mqtt = get_mqtt_service()
        if not mqtt:
            return False, "MQTT service is not available", None

        queued = mqtt.queue_command(actuator.feed_key, action)
        if not queued:
            EventLog.log_event(
                event_type=EventLog.TYPE_ERROR,
                description=f"Không thể gửi lệnh tới thiết bị: {actuator.name}",
                actuator_id=actuator.id,
                user_id=user_id,
                device_name=actuator.name,
                metadata={
                    'action': action,
                    'previous_mode': previous_mode,
                    'previous_value': previous_value,
                },
            )
            return False, "Không thể gửi lệnh tới controller/thiết bị", None

        actuator.current_value = action
        actuator.updated_at = datetime.utcnow()
        db.session.add(actuator)
        db.session.flush()

        EventLog.log_event(
            event_type=EventLog.TYPE_MANUAL if manual_override else EventLog.TYPE_AUTO,
            description=f"{'User' if manual_override else 'System'} set {actuator.name} to {action}",
            actuator_id=actuator.id,
            user_id=user_id,
            device_name=actuator.name,
            metadata={
                'action': action,
                'previous_mode': previous_mode,
                'new_mode': actuator.mode,
                'previous_value': previous_value,
                'new_value': actuator.current_value,
                'transport': 'mqtt_queue',
                'ack': 'queued',
            },
        )

        db.session.commit()

        return True, "", {
            'id': actuator.id,
            'name': actuator.name,
            'type': actuator.type,
            'mode': actuator.mode,
            'previous_mode': previous_mode,
            'current_value': actuator.current_value,
            'previous_value': previous_value,
            'is_on': actuator.is_on(),
            'updated_at': actuator.updated_at.isoformat() if actuator.updated_at else None,
            'ack': 'queued',
        }

    @staticmethod
    def set_actuator_mode(actuator_id: int, mode: str, user_id: int = None) -> Tuple[bool, str, Optional[dict]]:
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found", None

        if mode not in Actuator.VALID_MODES:
            return False, f"Invalid mode. Must be one of: {Actuator.VALID_MODES}", None

        old_mode = actuator.mode
        actuator.mode = mode
        actuator.updated_at = datetime.utcnow()
        db.session.add(actuator)
        db.session.flush()

        EventLog.log_event(
            event_type=EventLog.TYPE_MANUAL,
            description=f"Mode changed: {actuator.name} from {old_mode} to {mode}",
            actuator_id=actuator.id,
            user_id=user_id,
            device_name=actuator.name,
            metadata={'old_mode': old_mode, 'new_mode': mode},
        )

        db.session.commit()

        return True, "", {
            'id': actuator.id,
            'name': actuator.name,
            'mode': actuator.mode,
            'updated_at': actuator.updated_at.isoformat() if actuator.updated_at else None,
        }

    @staticmethod
    def toggle_actuator(actuator_id: int, user_id: int = None) -> Tuple[bool, str, Optional[dict]]:
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found", None

        if actuator.is_on():
            return ActuatorService.control_actuator(
                actuator_id,
                Actuator.ACTION_OFF,
                user_id=user_id,
                manual_override=True,
                auto_switch_to_manual=True,
            )

        return ActuatorService.control_actuator(
            actuator_id,
            Actuator.ACTION_ON,
            user_id=user_id,
            manual_override=True,
            auto_switch_to_manual=True,
        )

    @staticmethod
    def set_actuator_value(actuator_id: int, value: str, user_id: int = None) -> Tuple[bool, str, Optional[dict]]:
        return ActuatorService.control_actuator(
            actuator_id,
            str(value),
            user_id=user_id,
            manual_override=True,
            auto_switch_to_manual=True,
        )

    @staticmethod
    def get_actuator_status(actuator_id: int) -> Optional[dict]:
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return None

        return {
            'id': actuator.id,
            'name': actuator.name,
            'type': actuator.type,
            'current_value': actuator.current_value,
            'mode': actuator.mode,
            'is_on': actuator.is_on(),
            'last_updated': actuator.updated_at.isoformat() if actuator.updated_at else None,
        }

    @staticmethod
    def get_all_actuator_statuses() -> List[dict]:
        actuators = DeviceService.get_all_actuators()
        return [ActuatorService.get_actuator_status(a.id) for a in actuators]

    @staticmethod
    def execute_auto_action(actuator_id: int, action: str, reason: str = None) -> Tuple[bool, str]:
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found"

        if actuator.mode != Actuator.MODE_AUTO:
            return False, f"Actuator {actuator.name} is in MANUAL mode"

        success, error, _ = ActuatorService.control_actuator(
            actuator_id=actuator_id,
            action=action,
            user_id=None,
            manual_override=False,
            auto_switch_to_manual=False,
        )

        if success and reason:
            EventLog.log_event(
                event_type=EventLog.TYPE_AUTO,
                description=f"AUTO rule applied: {reason}",
                actuator_id=actuator.id,
                device_name=actuator.name,
                metadata={'action': action, 'reason': reason},
            )

        return success, error

