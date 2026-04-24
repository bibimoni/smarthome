<<<<<<< HEAD
"""Actuator service for device control operations."""
import logging
from typing import List, Optional, Tuple
from datetime import datetime
from app.extensions import db
from app.models.device import Actuator
from app.models.data import EventLog
=======
import logging
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from app.extensions import db
from app.models.device import Actuator
from app.models.data import EventLog
from app.services.device_service import DeviceService
>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f

logger = logging.getLogger(__name__)


<<<<<<< HEAD
=======
SERVO_COMMAND_COOLDOWN_SECONDS = 15


>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
def get_mqtt_service():
    """Get the MQTT service instance dynamically."""
    from app.services.mqtt_service import mqtt_service
    return mqtt_service


class ActuatorService:
    """Service class for actuator operations."""
<<<<<<< HEAD
    
    @staticmethod
    def get_all_actuators() -> List[Actuator]:
        """Get all active actuators."""
        return Actuator.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_actuator_by_id(actuator_id: int) -> Optional[Actuator]:
        """Get actuator by ID."""
        return Actuator.query.get(actuator_id)
    
    @staticmethod
    def get_actuator_by_feed_key(feed_key: str) -> Optional[Actuator]:
        """Get actuator by Adafruit feed key."""
        return Actuator.query.filter_by(feed_key=feed_key).first()
    
    @staticmethod
    def get_actuators_by_type(actuator_type: str) -> List[Actuator]:
        """Get all actuators of a specific type."""
        return Actuator.query.filter_by(type=actuator_type, is_active=True).all()
    
    @staticmethod
    def control_actuator(actuator_id: int, action: str, user_id: int = None,
                         manual_override: bool = True) -> Tuple[bool, str]:
        """
        Control an actuator.
        
        Args:
            actuator_id: Actuator ID
            action: Action to perform (ON, OFF, or value)
            user_id: User ID performing the action
            manual_override: If True, switch to MANUAL mode
            
        Returns:
            Tuple of (success, error message)
        """
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found"
        
        if not actuator.is_active:
            return False, "Actuator is not active"
        
        # Update actuator state
        actuator.current_value = action
        actuator.updated_at = datetime.utcnow()
        
        if manual_override:
            actuator.mode = Actuator.MODE_MANUAL
        
        # Send command via MQTT (publishes and queues for HTTP polling)
        mqtt = get_mqtt_service()
        if mqtt:
            logger.info(f"Sending command: feed_key={actuator.feed_key}, action={action}")
            # This publishes to MQTT AND queues for HTTP polling
            success = mqtt.queue_command(actuator.feed_key, action)
            logger.info(f"Command sent: {success}")
        else:
            logger.warning("MQTT service not available")
        
        # Log the event
=======

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

>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
        EventLog.log_event(
            event_type=EventLog.TYPE_MANUAL if manual_override else EventLog.TYPE_AUTO,
            description=f"{'User' if manual_override else 'System'} set {actuator.name} to {action}",
            actuator_id=actuator.id,
            user_id=user_id,
            device_name=actuator.name,
<<<<<<< HEAD
            metadata={'action': action, 'mode': actuator.mode}
        )
        
        db.session.commit()
        
        return True, ""
    
    @staticmethod
    def set_actuator_mode(actuator_id: int, mode: str, user_id: int = None) -> Tuple[bool, str]:
        """
        Set actuator mode (AUTO or MANUAL).
        
        Args:
            actuator_id: Actuator ID
            mode: Mode to set (AUTO or MANUAL)
            user_id: User ID performing the action
            
        Returns:
            Tuple of (success, error message)
        """
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found"
        
        if mode not in Actuator.VALID_MODES:
            return False, f"Invalid mode. Must be one of: {Actuator.VALID_MODES}"
        
        old_mode = actuator.mode
        actuator.mode = mode
        actuator.updated_at = datetime.utcnow()
        
        # Log the event
=======
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

>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
        EventLog.log_event(
            event_type=EventLog.TYPE_MANUAL,
            description=f"Mode changed: {actuator.name} from {old_mode} to {mode}",
            actuator_id=actuator.id,
            user_id=user_id,
            device_name=actuator.name,
<<<<<<< HEAD
            metadata={'old_mode': old_mode, 'new_mode': mode}
        )
        
        db.session.commit()
        
        return True, ""
    
    @staticmethod
    def toggle_actuator(actuator_id: int, user_id: int = None) -> Tuple[bool, str]:
        """
        Toggle actuator on/off.
        
        Args:
            actuator_id: Actuator ID
            user_id: User ID performing the action
            
        Returns:
            Tuple of (success, error message)
        """
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found"
        
        if actuator.is_on():
            return ActuatorService.control_actuator(actuator_id, Actuator.ACTION_OFF, user_id)
        else:
            return ActuatorService.control_actuator(actuator_id, Actuator.ACTION_ON, user_id)
    
    @staticmethod
    def set_actuator_value(actuator_id: int, value: str, user_id: int = None) -> Tuple[bool, str]:
        """
        Set actuator to a specific value (e.g., fan speed, RGB color).
        
        Args:
            actuator_id: Actuator ID
            value: Value to set
            user_id: User ID performing the action
            
        Returns:
            Tuple of (success, error message)
        """
        return ActuatorService.control_actuator(actuator_id, value, user_id)
    
    @staticmethod
    def get_actuator_status(actuator_id: int) -> Optional[dict]:
        """
        Get status of an actuator.
        
        Args:
            actuator_id: Actuator ID
            
        Returns:
            Actuator status dict or None
        """
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return None
        
=======
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

>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
        return {
            'id': actuator.id,
            'name': actuator.name,
            'type': actuator.type,
            'current_value': actuator.current_value,
            'mode': actuator.mode,
            'is_on': actuator.is_on(),
<<<<<<< HEAD
            'last_updated': actuator.updated_at.isoformat() if actuator.updated_at else None
        }
    
    @staticmethod
    def get_all_actuator_statuses() -> List[dict]:
        """
        Get status of all actuators.
        
        Returns:
            List of actuator status dicts
        """
        actuators = Actuator.query.filter_by(is_active=True).all()
        return [ActuatorService.get_actuator_status(a.id) for a in actuators]
    
    @staticmethod
    def execute_auto_action(actuator_id: int, action: str, reason: str = None) -> Tuple[bool, str]:
        """
        Execute an automatic action on an actuator.
        Only executes if actuator is in AUTO mode.
        
        Args:
            actuator_id: Actuator ID
            action: Action to perform
            reason: Reason for the action (for logging)
            
        Returns:
            Tuple of (success, error message)
        """
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return False, "Actuator not found"
        
        # Only execute if in AUTO mode
        if actuator.mode != Actuator.MODE_AUTO:
            return False, "Actuator is not in AUTO mode"
        
        # Update state
        actuator.current_value = action
        actuator.updated_at = datetime.utcnow()
        
        # Send command via MQTT
        if mqtt_service:
            mqtt_service.publish_actuator_command(actuator.feed_key, action)
        
        # Log the event
        EventLog.log_event(
            event_type=EventLog.TYPE_AUTO,
            description=reason or f"Auto control: {actuator.name} set to {action}",
            actuator_id=actuator.id,
            device_name=actuator.name,
            metadata={'action': action, 'auto': True}
        )
        
        db.session.commit()
        
        return True, ""
=======
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

>>>>>>> be1e4ea71bf986c0c527e009a8b815c2cf41e61f
