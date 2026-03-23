"""Automation models: ThresholdRule, Scene, SceneCondition, SceneAction."""
from datetime import datetime
from app.extensions import db


class ThresholdRule(db.Model):
    """Threshold rule model for automated device control based on sensor readings."""
    
    __tablename__ = 'threshold_rules'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id', ondelete='CASCADE'), nullable=False)
    operator = db.Column(db.String(5), nullable=False)  # '>', '<', '==', '>=', '<='
    threshold_value = db.Column(db.Float, nullable=False)
    actuator_id = db.Column(db.Integer, db.ForeignKey('actuators.id', ondelete='CASCADE'), nullable=False)
    action_value = db.Column(db.String(50), nullable=False)  # 'ON', 'OFF', or specific value
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Operator constants
    OP_GREATER = '>'
    OP_LESS = '<'
    OP_EQUAL = '=='
    OP_GREATER_EQUAL = '>='
    OP_LESS_EQUAL = '<='
    
    VALID_OPERATORS = [OP_GREATER, OP_LESS, OP_EQUAL, OP_GREATER_EQUAL, OP_LESS_EQUAL]
    
    def evaluate(self, current_value: float) -> bool:
        """
        Evaluate if the current sensor value triggers this rule.
        
        Args:
            current_value: Current sensor reading
            
        Returns:
            True if the rule condition is met
        """
        if current_value is None:
            return False
            
        if self.operator == self.OP_GREATER:
            return current_value > self.threshold_value
        elif self.operator == self.OP_LESS:
            return current_value < self.threshold_value
        elif self.operator == self.OP_EQUAL:
            return current_value == self.threshold_value
        elif self.operator == self.OP_GREATER_EQUAL:
            return current_value >= self.threshold_value
        elif self.operator == self.OP_LESS_EQUAL:
            return current_value <= self.threshold_value
        return False
    
    def get_condition_string(self) -> str:
        """Get a human-readable condition string."""
        sensor = self.sensor
        unit = sensor.unit if sensor else ''
        return f"{sensor.name if sensor else 'Sensor'} {self.operator} {self.threshold_value}{unit}"
    
    def to_dict(self) -> dict:
        """Convert threshold rule to dictionary."""
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'sensor_name': self.sensor.name if self.sensor else None,
            'operator': self.operator,
            'threshold_value': self.threshold_value,
            'actuator_id': self.actuator_id,
            'actuator_name': self.actuator.name if self.actuator else None,
            'action_value': self.action_value,
            'is_active': self.is_active,
            'description': self.description,
            'condition_string': self.get_condition_string(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<ThresholdRule sensor={self.sensor_id} {self.operator} {self.threshold_value}>'


class Scene(db.Model):
    """Scene model for grouping conditions and actions for automation scenarios."""
    
    __tablename__ = 'scenes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_triggered_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    conditions = db.relationship('SceneCondition', backref='scene', lazy=True, cascade='all, delete-orphan')
    actions = db.relationship('SceneAction', backref='scene', lazy=True, cascade='all, delete-orphan')
    
    def evaluate_conditions(self) -> bool:
        """
        Evaluate all conditions for this scene.
        All conditions must be met (AND logic).
        
        Returns:
            True if all conditions are met
        """
        if not self.conditions:
            return False
        
        for condition in self.conditions:
            if not condition.evaluate():
                return False
        return True
    
    def trigger(self) -> list:
        """
        Trigger all actions in this scene.
        
        Returns:
            List of executed SceneAction objects
        """
        executed_actions = []
        for action in self.actions:
            action.execute()
            executed_actions.append(action)
        
        self.last_triggered_at = datetime.utcnow()
        db.session.commit()
        
        return executed_actions
    
    def to_dict(self) -> dict:
        """Convert scene to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'last_triggered_at': self.last_triggered_at.isoformat() if self.last_triggered_at else None,
            'conditions': [c.to_dict() for c in self.conditions],
            'actions': [a.to_dict() for a in self.actions],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<Scene {self.name}>'


class SceneCondition(db.Model):
    """Scene condition model for defining when a scene should trigger."""
    
    __tablename__ = 'scene_conditions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scenes.id', ondelete='CASCADE'), nullable=False)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id', ondelete='CASCADE'), nullable=False)
    operator = db.Column(db.String(5), nullable=False)  # '>', '<', '==', '>=', '<='
    threshold_value = db.Column(db.Float, nullable=False)
    
    # Operator constants (same as ThresholdRule)
    OP_GREATER = '>'
    OP_LESS = '<'
    OP_EQUAL = '=='
    OP_GREATER_EQUAL = '>='
    OP_LESS_EQUAL = '<='
    
    VALID_OPERATORS = [OP_GREATER, OP_LESS, OP_EQUAL, OP_GREATER_EQUAL, OP_LESS_EQUAL]
    
    def evaluate(self) -> bool:
        """
        Evaluate if the current sensor value meets this condition.
        
        Returns:
            True if the condition is met
        """
        from app.models.device import SensorData
        
        sensor = self.sensor
        if not sensor:
            return False
        
        latest_data = sensor.get_latest_data()
        if not latest_data:
            return False
        
        current_value = latest_data.value
        
        if self.operator == self.OP_GREATER:
            return current_value > self.threshold_value
        elif self.operator == self.OP_LESS:
            return current_value < self.threshold_value
        elif self.operator == self.OP_EQUAL:
            return current_value == self.threshold_value
        elif self.operator == self.OP_GREATER_EQUAL:
            return current_value >= self.threshold_value
        elif self.operator == self.OP_LESS_EQUAL:
            return current_value <= self.threshold_value
        return False
    
    def get_condition_string(self) -> str:
        """Get a human-readable condition string."""
        sensor = self.sensor
        unit = sensor.unit if sensor else ''
        return f"{sensor.name if sensor else 'Sensor'} {self.operator} {self.threshold_value}{unit}"
    
    def to_dict(self) -> dict:
        """Convert scene condition to dictionary."""
        return {
            'id': self.id,
            'scene_id': self.scene_id,
            'sensor_id': self.sensor_id,
            'sensor_name': self.sensor.name if self.sensor else None,
            'operator': self.operator,
            'threshold_value': self.threshold_value,
            'condition_string': self.get_condition_string(),
        }
    
    def __repr__(self):
        return f'<SceneCondition sensor={self.sensor_id} {self.operator} {self.threshold_value}>'


class SceneAction(db.Model):
    """Scene action model for defining what actions to execute when a scene triggers."""
    
    __tablename__ = 'scene_actions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scene_id = db.Column(db.Integer, db.ForeignKey('scenes.id', ondelete='CASCADE'), nullable=False)
    actuator_id = db.Column(db.Integer, db.ForeignKey('actuators.id', ondelete='CASCADE'), nullable=False)
    action_value = db.Column(db.String(50), nullable=False)  # 'ON', 'OFF', or specific value
    
    def execute(self):
        """Execute this action on the associated actuator."""
        from app.services.mqtt_service import MQTTService
        
        actuator = self.actuator
        if not actuator:
            return False
        
        # Update actuator state in database
        actuator.current_value = self.action_value
        actuator.updated_at = datetime.utcnow()
        
        # Send command via MQTT
        mqtt_service = MQTTService.get_instance()
        if mqtt_service:
            mqtt_service.publish_actuator_command(actuator.feed_key, self.action_value)
        
        db.session.commit()
        
        # Log the event
        from app.models.data import EventLog
        EventLog.log_event(
            event_type=EventLog.TYPE_SCENE,
            description=f"Scene '{self.scene.name}': {actuator.name} set to {self.action_value}",
            actuator_id=actuator.id,
            user_id=self.scene.user_id,
            device_name=actuator.name,
            metadata={'scene_id': self.scene_id, 'action_value': self.action_value}
        )
        
        return True
    
    def get_action_string(self) -> str:
        """Get a human-readable action string."""
        actuator = self.actuator
        return f"{actuator.name if actuator else 'Actuator'} → {self.action_value}"
    
    def to_dict(self) -> dict:
        """Convert scene action to dictionary."""
        return {
            'id': self.id,
            'scene_id': self.scene_id,
            'actuator_id': self.actuator_id,
            'actuator_name': self.actuator.name if self.actuator else None,
            'action_value': self.action_value,
            'action_string': self.get_action_string(),
        }
    
    def __repr__(self):
        return f'<SceneAction actuator={self.actuator_id} → {self.action_value}>'