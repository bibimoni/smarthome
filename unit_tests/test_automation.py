import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from app.models.automation import ThresholdRule, Scene, SceneCondition, SceneAction


class TestThresholdRule:
    def test_evaluate_greater_than_true(self):
        rule = ThresholdRule(operator='>', threshold_value=30.0)
        assert rule.evaluate(35.0) is True
    
    def test_evaluate_greater_than_false(self):
        rule = ThresholdRule(operator='>', threshold_value=30.0)
        assert rule.evaluate(25.0) is False
    
    def test_evaluate_less_than_true(self):
        rule = ThresholdRule(operator='<', threshold_value=30.0)
        assert rule.evaluate(25.0) is True
    
    def test_evaluate_less_than_false(self):
        rule = ThresholdRule(operator='<', threshold_value=30.0)
        assert rule.evaluate(35.0) is False
    
    def test_evaluate_equal_true(self):
        rule = ThresholdRule(operator='==', threshold_value=30.0)
        assert rule.evaluate(30.0) is True
    
    def test_evaluate_equal_false(self):
        rule = ThresholdRule(operator='==', threshold_value=30.0)
        assert rule.evaluate(31.0) is False
    
    def test_evaluate_greater_equal_true(self):
        rule = ThresholdRule(operator='>=', threshold_value=30.0)
        assert rule.evaluate(30.0) is True
        assert rule.evaluate(35.0) is True
    
    def test_evaluate_greater_equal_false(self):
        rule = ThresholdRule(operator='>=', threshold_value=30.0)
        assert rule.evaluate(25.0) is False
    
    def test_evaluate_less_equal_true(self):
        rule = ThresholdRule(operator='<=', threshold_value=30.0)
        assert rule.evaluate(30.0) is True
        assert rule.evaluate(25.0) is True
    
    def test_evaluate_less_equal_false(self):
        rule = ThresholdRule(operator='<=', threshold_value=30.0)
        assert rule.evaluate(35.0) is False
    
    def test_evaluate_none_value(self):
        rule = ThresholdRule(operator='>', threshold_value=30.0)
        assert rule.evaluate(None) is False
    
    def test_valid_operators(self):
        assert '>' in ThresholdRule.VALID_OPERATORS
        assert '<' in ThresholdRule.VALID_OPERATORS
        assert '==' in ThresholdRule.VALID_OPERATORS
        assert '>=' in ThresholdRule.VALID_OPERATORS
        assert '<=' in ThresholdRule.VALID_OPERATORS
    
    def test_to_dict(self):
        rule = ThresholdRule(
            id=1,
            sensor_id=1,
            operator='>',
            threshold_value=30.0,
            actuator_id=1,
            action_value='ON',
            is_active=True,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1)
        )
        rule.sensor = MagicMock(name='Temperature', unit='°C')
        rule.actuator = MagicMock(name='Fan')
        result = rule.to_dict()
        assert result['id'] == 1
        assert result['operator'] == '>'
        assert result['threshold_value'] == 30.0
        assert result['action_value'] == 'ON'


class TestScene:
    def test_evaluate_conditions_empty(self):
        scene = Scene()
        scene.conditions = []
        assert scene.evaluate_conditions() is False
    
    def test_evaluate_conditions_all_true(self):
        scene = Scene()
        condition1 = MagicMock()
        condition1.evaluate.return_value = True
        condition2 = MagicMock()
        condition2.evaluate.return_value = True
        scene.conditions = [condition1, condition2]
        assert scene.evaluate_conditions() is True
    
    def test_evaluate_conditions_one_false(self):
        scene = Scene()
        condition1 = MagicMock()
        condition1.evaluate.return_value = True
        condition2 = MagicMock()
        condition2.evaluate.return_value = False
        scene.conditions = [condition1, condition2]
        assert scene.evaluate_conditions() is False
    
    def test_to_dict(self):
        scene = Scene(
            id=1,
            user_id=1,
            name='Good Night',
            description='Turn off lights',
            is_active=True,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1)
        )
        scene.conditions = []
        scene.actions = []
        result = scene.to_dict()
        assert result['id'] == 1
        assert result['name'] == 'Good Night'
        assert result['is_active'] is True
    
    def test_repr(self):
        scene = Scene(name='Good Night')
        assert 'Good Night' in repr(scene)


class TestSceneCondition:
    def test_valid_operators(self):
        assert '>' in SceneCondition.VALID_OPERATORS
        assert '<' in SceneCondition.VALID_OPERATORS
        assert '==' in SceneCondition.VALID_OPERATORS
    
    def test_to_dict(self):
        condition = SceneCondition(
            id=1,
            scene_id=1,
            sensor_id=1,
            operator='>',
            threshold_value=30.0
        )
        condition.sensor = MagicMock(name='Temperature', unit='°C')
        result = condition.to_dict()
        assert result['id'] == 1
        assert result['operator'] == '>'
        assert result['threshold_value'] == 30.0


class TestSceneAction:
    def test_to_dict(self):
        action = SceneAction(
            id=1,
            scene_id=1,
            actuator_id=1,
            action_value='ON'
        )
        action.actuator = MagicMock(name='Fan')
        result = action.to_dict()
        assert result['id'] == 1
        assert result['actuator_id'] == 1
        assert result['action_value'] == 'ON'
    
    def test_repr(self):
        action = SceneAction(actuator_id=1, action_value='ON')
        assert 'actuator=1' in repr(action)
        assert 'ON' in repr(action)
