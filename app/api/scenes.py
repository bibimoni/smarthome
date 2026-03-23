"""Scene API endpoints.

Use Case: UC-5 Create and run device control scenarios with conditions and actions
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.scene_service import SceneService

scenes_bp = Blueprint('scenes', __name__)


@scenes_bp.route('/', methods=['GET'])
@jwt_required()
def get_scenes():
    """
    Get all scenes for the current user.
    
    UC-5: Scene management
    ---
    tags:
      - Scenes
    summary: Get all scenes
    security:
      - Bearer: []
    responses:
      200:
        description: List of scenes
        schema:
          type: object
          properties:
            scenes:
              type: array
              items:
                $ref: "#/definitions/Scene"
            count:
              type: integer
    """
    user_id = get_jwt_identity()
    scenes = SceneService.get_all_scenes(user_id)
    
    return jsonify({
        'scenes': [s.to_dict() for s in scenes],
        'count': len(scenes)
    }), 200


@scenes_bp.route('/<int:scene_id>', methods=['GET'])
@jwt_required()
def get_scene(scene_id):
    """
    Get a specific scene.
    
    ---
    tags:
      - Scenes
    summary: Get scene by ID
    security:
      - Bearer: []
    parameters:
      - name: scene_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Scene details
        schema:
          type: object
          properties:
            scene:
              $ref: "#/definitions/Scene"
      404:
        description: Scene not found
        schema:
          $ref: "#/definitions/Error"
    """
    scene = SceneService.get_scene_by_id(scene_id)
    
    if not scene:
        return jsonify({'error': 'Scene not found'}), 404
    
    return jsonify({'scene': scene.to_dict()}), 200


@scenes_bp.route('/<int:scene_id>/status', methods=['GET'])
@jwt_required()
def get_scene_status(scene_id):
    """
    Get status of a scene including condition evaluation.
    
    ---
    tags:
      - Scenes
    summary: Get scene status
    security:
      - Bearer: []
    parameters:
      - name: scene_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Scene status
        schema:
          type: object
          properties:
            status:
              type: object
      404:
        description: Scene not found
        schema:
          $ref: "#/definitions/Error"
    """
    status = SceneService.get_scene_status(scene_id)
    
    if not status:
        return jsonify({'error': 'Scene not found'}), 404
    
    return jsonify({'status': status}), 200


@scenes_bp.route('/', methods=['POST'])
@jwt_required()
def create_scene():
    """
    Create a new scene.
    
    UC-5: Create and run device control scenarios
    ---
    tags:
      - Scenes
    summary: Create a new scene
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: "Good Night"
            description:
              type: string
              example: "Turn off all lights and lower temperature"
            conditions:
              type: array
              items:
                $ref: "#/definitions/SceneCondition"
            actions:
              type: array
              items:
                $ref: "#/definitions/SceneAction"
    responses:
      201:
        description: Scene created
        schema:
          type: object
          properties:
            message:
              type: string
            scene:
              $ref: "#/definitions/Scene"
      400:
        description: Validation error
        schema:
          $ref: "#/definitions/Error"
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    scene, error = SceneService.create_scene(
        user_id=user_id,
        name=data.get('name'),
        description=data.get('description'),
        conditions=data.get('conditions'),
        actions=data.get('actions')
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Scene created',
        'scene': scene.to_dict()
    }), 201


@scenes_bp.route('/<int:scene_id>', methods=['PUT'])
@jwt_required()
def update_scene(scene_id):
    """
    Update a scene.
    
    UC-5: Scene management
    ---
    tags:
      - Scenes
    summary: Update a scene
    security:
      - Bearer: []
    parameters:
      - name: scene_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            is_active:
              type: boolean
    responses:
      200:
        description: Scene updated
        schema:
          type: object
          properties:
            message:
              type: string
            scene:
              $ref: "#/definitions/Scene"
      400:
        description: Validation error
        schema:
          $ref: "#/definitions/Error"
      404:
        description: Scene not found
        schema:
          $ref: "#/definitions/Error"
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    scene, error = SceneService.update_scene(
        scene_id=scene_id,
        name=data.get('name'),
        description=data.get('description'),
        is_active=data.get('is_active')
    )
    
    if error:
        return jsonify({'error': error}), 404 if 'not found' in error else 400
    
    return jsonify({
        'message': 'Scene updated',
        'scene': scene.to_dict()
    }), 200


@scenes_bp.route('/<int:scene_id>', methods=['DELETE'])
@jwt_required()
def delete_scene(scene_id):
    """
    Delete a scene.
    
    UC-5: Scene management
    ---
    tags:
      - Scenes
    summary: Delete a scene
    security:
      - Bearer: []
    parameters:
      - name: scene_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Scene deleted
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Scene not found
        schema:
          $ref: "#/definitions/Error"
    """
    success, error = SceneService.delete_scene(scene_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({'message': 'Scene deleted'}), 200


@scenes_bp.route('/<int:scene_id>/execute', methods=['POST'])
@jwt_required()
def execute_scene(scene_id):
    """
    Manually execute a scene.
    
    UC-5: Run scene
    ---
    tags:
      - Scenes
    summary: Execute a scene
    security:
      - Bearer: []
    parameters:
      - name: scene_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Scene executed
        schema:
          type: object
          properties:
            message:
              type: string
            scene_id:
              type: integer
      400:
        description: Scene not active or execution error
        schema:
          $ref: "#/definitions/Error"
      404:
        description: Scene not found
        schema:
          $ref: "#/definitions/Error"
    """
    user_id = get_jwt_identity()
    
    success, error = SceneService.execute_scene(scene_id, user_id)
    
    if error:
        return jsonify({'error': error}), 404 if 'not found' in error else 400
    
    return jsonify({
        'message': 'Scene executed successfully',
        'scene_id': scene_id
    }), 200


@scenes_bp.route('/<int:scene_id>/conditions', methods=['POST'])
@jwt_required()
def add_condition(scene_id):
    """
    Add a condition to a scene.
    
    UC-5: Scene condition management
    
    Request Body:
        sensor_id: Sensor ID
        operator: Comparison operator (>, <, ==, >=, <=)
        threshold_value: Threshold value
        
    Returns:
        201: Condition added
        400: Validation error
        404: Scene or sensor not found
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    condition, error = SceneService.add_condition(
        scene_id=scene_id,
        sensor_id=data.get('sensor_id'),
        operator=data.get('operator'),
        threshold_value=data.get('threshold_value')
    )
    
    if error:
        return jsonify({'error': error}), 404 if 'not found' in error else 400
    
    return jsonify({
        'message': 'Condition added',
        'condition': condition.to_dict()
    }), 201


@scenes_bp.route('/<int:scene_id>/conditions/<int:condition_id>', methods=['DELETE'])
@jwt_required()
def remove_condition(scene_id, condition_id):
    """
    Remove a condition from a scene.
    
    UC-5: Scene condition management
    
    Returns:
        200: Condition removed
        404: Condition not found
    """
    success, error = SceneService.remove_condition(condition_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({'message': 'Condition removed'}), 200


@scenes_bp.route('/<int:scene_id>/actions', methods=['POST'])
@jwt_required()
def add_action(scene_id):
    """
    Add an action to a scene.
    
    UC-5: Scene action management
    
    Request Body:
        actuator_id: Actuator ID
        action_value: Action value (ON, OFF, etc.)
        
    Returns:
        201: Action added
        400: Validation error
        404: Scene or actuator not found
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    action, error = SceneService.add_action(
        scene_id=scene_id,
        actuator_id=data.get('actuator_id'),
        action_value=data.get('action_value')
    )
    
    if error:
        return jsonify({'error': error}), 404 if 'not found' in error else 400
    
    return jsonify({
        'message': 'Action added',
        'action': action.to_dict()
    }), 201


@scenes_bp.route('/<int:scene_id>/actions/<int:action_id>', methods=['DELETE'])
@jwt_required()
def remove_action(scene_id, action_id):
    """
    Remove an action from a scene.
    
    UC-5: Scene action management
    
    Returns:
        200: Action removed
        404: Action not found
    """
    success, error = SceneService.remove_action(action_id)
    
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({'message': 'Action removed'}), 200


@scenes_bp.route('/check', methods=['POST'])
@jwt_required()
def check_scenes():
    """
    Check all active scenes and execute if conditions are met.
    This endpoint is typically called by the system or scheduler.
    
    Returns:
        200: Scenes checked
    """
    SceneService.check_and_execute_scenes()
    
    return jsonify({'message': 'Scenes checked'}), 200