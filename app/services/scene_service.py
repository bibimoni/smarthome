"""Scene service for automation scenario management."""
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from app.extensions import db
from app.models.automation import Scene, SceneCondition, SceneAction
from app.models.device import Sensor, Actuator
from app.models.data import EventLog


class SceneService:
    """Service class for scene management operations."""
    
    @staticmethod
    def get_all_scenes(user_id: int = None) -> List[Scene]:
        """
        Get all scenes.
        
        Args:
            user_id: Optional user ID to filter scenes
            
        Returns:
            List of Scene objects
        """
        query = Scene.query.filter_by(is_active=True)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.all()
    
    @staticmethod
    def get_scene_by_id(scene_id: int) -> Optional[Scene]:
        """Get scene by ID."""
        return Scene.query.get(scene_id)
    
    @staticmethod
    def create_scene(user_id: int, name: str, description: str = None,
                     conditions: List[Dict] = None, actions: List[Dict] = None) -> Tuple[Optional[Scene], str]:
        """
        Create a new scene with conditions and actions.
        
        Args:
            user_id: User ID creating the scene
            name: Scene name
            description: Scene description
            conditions: List of condition dicts with sensor_id, operator, threshold_value
            actions: List of action dicts with actuator_id, action_value
            
        Returns:
            Tuple of (Scene or None, error message)
        """
        # Validate scene name
        if not name or len(name.strip()) == 0:
            return None, "Scene name is required"
        
        # Create scene
        scene = Scene(
            user_id=user_id,
            name=name.strip(),
            description=description,
            is_active=True
        )
        
        db.session.add(scene)
        db.session.flush()  # Get scene ID
        
        # Add conditions
        if conditions:
            for cond in conditions:
                sensor = Sensor.query.get(cond.get('sensor_id'))
                if not sensor:
                    return None, f"Sensor {cond.get('sensor_id')} not found"
                
                if cond.get('operator') not in SceneCondition.VALID_OPERATORS:
                    return None, f"Invalid operator: {cond.get('operator')}"
                
                condition = SceneCondition(
                    scene_id=scene.id,
                    sensor_id=cond['sensor_id'],
                    operator=cond['operator'],
                    threshold_value=cond['threshold_value']
                )
                db.session.add(condition)
        
        # Add actions
        if actions:
            for act in actions:
                actuator = Actuator.query.get(act.get('actuator_id'))
                if not actuator:
                    return None, f"Actuator {act.get('actuator_id')} not found"
                
                action = SceneAction(
                    scene_id=scene.id,
                    actuator_id=act['actuator_id'],
                    action_value=act['action_value']
                )
                db.session.add(action)
        
        db.session.commit()
        
        # Log scene creation
        EventLog.log_event(
            event_type=EventLog.TYPE_SCENE,
            description=f"Scene '{name}' created",
            user_id=user_id,
            metadata={'scene_id': scene.id, 'action': 'create'}
        )
        
        return scene, ""
    
    @staticmethod
    def update_scene(scene_id: int, name: str = None, description: str = None,
                     is_active: bool = None) -> Tuple[Optional[Scene], str]:
        """Update scene properties."""
        scene = Scene.query.get(scene_id)
        if not scene:
            return None, "Scene not found"
        
        if name is not None:
            if not name or len(name.strip()) == 0:
                return None, "Scene name cannot be empty"
            scene.name = name.strip()
        
        if description is not None:
            scene.description = description
        
        if is_active is not None:
            scene.is_active = is_active
        
        scene.updated_at = datetime.utcnow()
        db.session.commit()
        
        return scene, ""
    
    @staticmethod
    def delete_scene(scene_id: int) -> Tuple[bool, str]:
        """Delete a scene."""
        scene = Scene.query.get(scene_id)
        if not scene:
            return False, "Scene not found"
        
        scene.is_active = False
        db.session.commit()
        
        return True, ""
    
    @staticmethod
    def add_condition(scene_id: int, sensor_id: int, operator: str, 
                      threshold_value: float) -> Tuple[Optional[SceneCondition], str]:
        """
        Add a condition to a scene.
        
        Args:
            scene_id: Scene ID
            sensor_id: Sensor ID
            operator: Comparison operator
            threshold_value: Threshold value
            
        Returns:
            Tuple of (SceneCondition or None, error message)
        """
        scene = Scene.query.get(scene_id)
        if not scene:
            return None, "Scene not found"
        
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            return None, "Sensor not found"
        
        if operator not in SceneCondition.VALID_OPERATORS:
            return None, f"Invalid operator. Must be one of: {SceneCondition.VALID_OPERATORS}"
        
        condition = SceneCondition(
            scene_id=scene_id,
            sensor_id=sensor_id,
            operator=operator,
            threshold_value=threshold_value
        )
        
        db.session.add(condition)
        db.session.commit()
        
        return condition, ""
    
    @staticmethod
    def remove_condition(condition_id: int) -> Tuple[bool, str]:
        """Remove a condition from a scene."""
        condition = SceneCondition.query.get(condition_id)
        if not condition:
            return False, "Condition not found"
        
        db.session.delete(condition)
        db.session.commit()
        
        return True, ""
    
    @staticmethod
    def add_action(scene_id: int, actuator_id: int, 
                   action_value: str) -> Tuple[Optional[SceneAction], str]:
        """
        Add an action to a scene.
        
        Args:
            scene_id: Scene ID
            actuator_id: Actuator ID
            action_value: Action value (ON, OFF, etc.)
            
        Returns:
            Tuple of (SceneAction or None, error message)
        """
        scene = Scene.query.get(scene_id)
        if not scene:
            return None, "Scene not found"
        
        actuator = Actuator.query.get(actuator_id)
        if not actuator:
            return None, "Actuator not found"
        
        action = SceneAction(
            scene_id=scene_id,
            actuator_id=actuator_id,
            action_value=action_value
        )
        
        db.session.add(action)
        db.session.commit()
        
        return action, ""
    
    @staticmethod
    def remove_action(action_id: int) -> Tuple[bool, str]:
        """Remove an action from a scene."""
        action = SceneAction.query.get(action_id)
        if not action:
            return False, "Action not found"
        
        db.session.delete(action)
        db.session.commit()
        
        return True, ""
    
    @staticmethod
    def execute_scene(scene_id: int, user_id: int = None) -> Tuple[bool, str]:
        """
        Manually execute a scene.
        
        Args:
            scene_id: Scene ID
            user_id: User ID executing the scene
            
        Returns:
            Tuple of (success, error message)
        """
        scene = Scene.query.get(scene_id)
        if not scene:
            return False, "Scene not found"
        
        if not scene.is_active:
            return False, "Scene is not active"
        
        # Execute all actions
        try:
            executed_actions = scene.trigger()
            
            # Log scene execution
            EventLog.log_event(
                event_type=EventLog.TYPE_SCENE,
                description=f"Scene '{scene.name}' executed manually",
                user_id=user_id,
                metadata={
                    'scene_id': scene.id,
                    'actions_count': len(executed_actions),
                    'trigger': 'manual'
                }
            )
            
            return True, ""
        except Exception as e:
            return False, f"Error executing scene: {str(e)}"
    
    @staticmethod
    def check_and_execute_scenes():
        """
        Check all active scenes and execute if conditions are met.
        This should be called periodically (e.g., when new sensor data arrives).
        """
        scenes = Scene.query.filter_by(is_active=True).all()
        
        for scene in scenes:
            try:
                if scene.evaluate_conditions():
                    # Check if scene was recently triggered (avoid duplicate triggers)
                    if scene.last_triggered_at:
                        time_since = datetime.utcnow() - scene.last_triggered_at
                        if time_since.total_seconds() < 60:  # 1 minute cooldown
                            continue
                    
                    scene.trigger()
                    
                    EventLog.log_event(
                        event_type=EventLog.TYPE_SCENE,
                        description=f"Scene '{scene.name}' triggered automatically",
                        user_id=scene.user_id,
                        metadata={
                            'scene_id': scene.id,
                            'trigger': 'automatic'
                        }
                    )
            except Exception as e:
                print(f"Error checking scene {scene.id}: {e}")
    
    @staticmethod
    def get_scene_status(scene_id: int) -> Optional[dict]:
        """
        Get status of a scene including condition evaluation.
        
        Args:
            scene_id: Scene ID
            
        Returns:
            Status dict or None
        """
        scene = Scene.query.get(scene_id)
        if not scene:
            return None
        
        conditions_met = scene.evaluate_conditions()
        
        return {
            'id': scene.id,
            'name': scene.name,
            'is_active': scene.is_active,
            'conditions_met': conditions_met,
            'last_triggered_at': scene.last_triggered_at.isoformat() if scene.last_triggered_at else None,
            'conditions': [c.to_dict() for c in scene.conditions],
            'actions': [a.to_dict() for a in scene.actions]
        }