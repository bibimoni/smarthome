"""Threshold service for automation rules management."""
from typing import List, Optional, Tuple
from datetime import datetime
from app.extensions import db
from app.models.automation import ThresholdRule
from app.models.device import Sensor, Actuator
from app.models.data import EventLog
from app.services.mqtt_service import mqtt_service


class ThresholdService:
    """Service class for threshold rule management."""
    
    @staticmethod
    def get_all_rules(is_active: bool = None) -> List[ThresholdRule]:
        """
        Get all threshold rules.
        
        Args:
            is_active: Optional filter by active status
            
        Returns:
            List of ThresholdRule objects
        """
        query = ThresholdRule.query
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        return query.all()
    
    @staticmethod
    def get_rules_for_sensor(sensor_id: int) -> List[ThresholdRule]:
        """Get all rules for a specific sensor."""
        return ThresholdRule.query.filter_by(sensor_id=sensor_id).all()
    
    @staticmethod
    def get_rules_for_actuator(actuator_id: int) -> List[ThresholdRule]:
        """Get all rules controlling a specific actuator."""
        return ThresholdRule.query.filter_by(actuator_id=actuator_id).all()
    
    @staticmethod
    def get_rule_by_id(rule_id: int) -> Optional[ThresholdRule]:
        """Get threshold rule by ID."""
        return ThresholdRule.query.get(rule_id)
    
    @staticmethod
    def create_rule(sensor_id: int, operator: str, threshold_value: float,
                    actuator_id: int, action_value: str, 
                    description: str = None) -> Tuple[Optional[ThresholdRule], str]:
        """
        Create a new threshold rule.
        
        Args:
            sensor_id: Sensor ID to monitor
            operator: Comparison operator (>, <, ==, >=, <=)
            threshold_value: Threshold value
            actuator_id: Actuator ID to control
            action_value: Action to perform when rule triggers
            description: Optional description
            
        Returns:
            Tuple of (ThresholdRule or None, error message)
        """
        # Validate sensor
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            return None, "Sensor not found"
        
        # Validate actuator
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return None, "Actuator not found"
        
        # Validate operator
        if operator not in ThresholdRule.VALID_OPERATORS:
            return None, f"Invalid operator. Must be one of: {ThresholdRule.VALID_OPERATORS}"
        
        # Create rule
        rule = ThresholdRule(
            sensor_id=sensor_id,
            operator=operator,
            threshold_value=threshold_value,
            actuator_id=actuator_id,
            action_value=action_value,
            description=description,
            is_active=True
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return rule, ""
    
    @staticmethod
    def update_rule(rule_id: int, operator: str = None, threshold_value: float = None,
                    action_value: str = None, description: str = None,
                    is_active: bool = None) -> Tuple[Optional[ThresholdRule], str]:
        """
        Update a threshold rule.
        
        Args:
            rule_id: Rule ID
            operator: New operator
            threshold_value: New threshold value
            action_value: New action value
            description: New description
            is_active: New active status
            
        Returns:
            Tuple of (ThresholdRule or None, error message)
        """
        rule = ThresholdRule.query.get(rule_id)
        if not rule:
            return None, "Rule not found"
        
        if operator is not None:
            if operator not in ThresholdRule.VALID_OPERATORS:
                return None, f"Invalid operator. Must be one of: {ThresholdRule.VALID_OPERATORS}"
            rule.operator = operator
        
        if threshold_value is not None:
            rule.threshold_value = threshold_value
        
        if action_value is not None:
            rule.action_value = action_value
        
        if description is not None:
            rule.description = description
        
        if is_active is not None:
            rule.is_active = is_active
        
        rule.updated_at = datetime.utcnow()
        db.session.commit()
        
        return rule, ""
    
    @staticmethod
    def delete_rule(rule_id: int) -> Tuple[bool, str]:
        """Delete a threshold rule."""
        rule = ThresholdRule.query.get(rule_id)
        if not rule:
            return False, "Rule not found"
        
        db.session.delete(rule)
        db.session.commit()
        
        return True, ""
    
    @staticmethod
    def toggle_rule(rule_id: int) -> Tuple[Optional[ThresholdRule], str]:
        """
        Toggle a rule active/inactive.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Tuple of (ThresholdRule or None, error message)
        """
        rule = ThresholdRule.query.get(rule_id)
        if not rule:
            return None, "Rule not found"
        
        rule.is_active = not rule.is_active
        rule.updated_at = datetime.utcnow()
        db.session.commit()
        
        return rule, ""
    
    @staticmethod
    def evaluate_rule(rule_id: int) -> Tuple[bool, Optional[str]]:
        """
        Evaluate a rule against current sensor value.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Tuple of (condition_met, action_to_take)
        """
        rule = ThresholdRule.query.get(rule_id)
        if not rule:
            return False, None
        
        if not rule.is_active:
            return False, None
        
        # Get latest sensor data
        sensor = rule.sensor
        latest_data = sensor.get_latest_data()
        
        if not latest_data:
            return False, None
        
        # Evaluate condition
        if rule.evaluate(latest_data.value):
            return True, rule.action_value
        
        return False, None
    
    @staticmethod
    def evaluate_and_execute(rule_id: int) -> Tuple[bool, str]:
        """
        Evaluate a rule and execute action if condition is met.
        Only executes if actuator is in AUTO mode.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Tuple of (executed, message)
        """
        rule = ThresholdRule.query.get(rule_id)
        if not rule:
            return False, "Rule not found"
        
        if not rule.is_active:
            return False, "Rule is not active"
        
        # Check actuator mode
        actuator = rule.actuator
        if actuator.mode != Actuator.MODE_AUTO:
            return False, f"Actuator {actuator.name} is in MANUAL mode"
        
        # Get latest sensor data
        sensor = rule.sensor
        latest_data = sensor.get_latest_data()
        
        if not latest_data:
            return False, "No sensor data available"
        
        # Evaluate condition
        if not rule.evaluate(latest_data.value):
            return False, "Condition not met"
        
        # Execute action
        current_value = actuator.current_value
        
        # Don't send the same command repeatedly
        if current_value == rule.action_value:
            return False, "Already in desired state"
        
        # Update actuator state
        actuator.current_value = rule.action_value
        actuator.updated_at = datetime.utcnow()
        
        # Send command via MQTT
        if mqtt_service:
            mqtt_service.publish_actuator_command(actuator.feed_key, rule.action_value)
        
        # Log the event
        EventLog.log_event(
            event_type=EventLog.TYPE_AUTO,
            description=f"{rule.get_condition_string()}: {actuator.name} set to {rule.action_value}",
            actuator_id=actuator.id,
            device_name=actuator.name,
            metadata={
                'rule_id': rule.id,
                'sensor_value': latest_data.value,
                'action_value': rule.action_value
            }
        )
        
        db.session.commit()
        
        return True, f"Executed: {actuator.name} set to {rule.action_value}"
    
    @staticmethod
    def evaluate_all_rules() -> dict:
        """
        Evaluate all active rules and execute actions where conditions are met.
        
        Returns:
            Dict with evaluation results
        """
        rules = ThresholdRule.query.filter_by(is_active=True).all()
        results = {
            'executed': [],
            'skipped': [],
            'errors': []
        }
        
        for rule in rules:
            try:
                executed, message = ThresholdService.evaluate_and_execute(rule.id)
                if executed:
                    results['executed'].append({
                        'rule_id': rule.id,
                        'message': message
                    })
                else:
                    results['skipped'].append({
                        'rule_id': rule.id,
                        'reason': message
                    })
            except Exception as e:
                results['errors'].append({
                    'rule_id': rule.id,
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def get_rule_status(rule_id: int) -> Optional[dict]:
        """
        Get status of a threshold rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Status dict or None
        """
        rule = ThresholdRule.query.get(rule_id)
        if not rule:
            return None
        
        sensor = rule.sensor
        latest_data = sensor.get_latest_data() if sensor else None
        
        condition_met = False
        if latest_data:
            condition_met = rule.evaluate(latest_data.value)
        
        return {
            'id': rule.id,
            'sensor': {
                'id': sensor.id,
                'name': sensor.name,
                'type': sensor.type,
                'current_value': latest_data.value if latest_data else None,
                'unit': sensor.unit
            },
            'condition': rule.get_condition_string(),
            'condition_met': condition_met,
            'actuator': {
                'id': rule.actuator.id,
                'name': rule.actuator.name,
                'current_value': rule.actuator.current_value,
                'mode': rule.actuator.mode
            },
            'action_value': rule.action_value,
            'is_active': rule.is_active
        }