"""Actuator service for device control operations."""
import logging
from typing import List, Optional, Tuple
from datetime import datetime
from app.extensions import db
from app.models.device import Actuator
from app.models.data import EventLog
from app.services.mqtt_service import mqtt_service

logger = logging.getLogger(__name__)


class ActuatorService:
    """Service class for actuator operations."""
    
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
        
        # Send command via MQTT
        if mqtt_service:
            logger.info(f"Publishing MQTT command: feed_key={actuator.feed_key}, action={action}")
            success = mqtt_service.publish_actuator_command(actuator.feed_key, action)
            logger.info(f"MQTT publish result: {success}")
        else:
            logger.warning("MQTT service not available")
        
        # Log the event
        EventLog.log_event(
            event_type=EventLog.TYPE_MANUAL if manual_override else EventLog.TYPE_AUTO,
            description=f"{'User' if manual_override else 'System'} set {actuator.name} to {action}",
            actuator_id=actuator.id,
            user_id=user_id,
            device_name=actuator.name,
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
        EventLog.log_event(
            event_type=EventLog.TYPE_MANUAL,
            description=f"Mode changed: {actuator.name} from {old_mode} to {mode}",
            actuator_id=actuator.id,
            user_id=user_id,
            device_name=actuator.name,
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
        
        return {
            'id': actuator.id,
            'name': actuator.name,
            'type': actuator.type,
            'current_value': actuator.current_value,
            'mode': actuator.mode,
            'is_on': actuator.is_on(),
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