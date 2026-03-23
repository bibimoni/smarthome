"""Event Log API endpoints.

Use Case: UC-4 View activity history/logs with filtering
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.data import EventLog

logs_bp = Blueprint('logs', __name__)


@logs_bp.route('/', methods=['GET'])
@jwt_required()
def get_logs():
    """
    Get event logs with filtering and pagination.
    
    UC-4: View activity history
    ---
    tags:
      - Logs
    summary: Get event logs
    security:
      - Bearer: []
    parameters:
      - name: event_type
        in: query
        type: string
        enum: [ALERT, AUTO, MANUAL, ERROR, SCENE]
      - name: actuator_id
        in: query
        type: integer
      - name: user_id
        in: query
        type: integer
      - name: start_date
        in: query
        type: string
        format: date-time
      - name: end_date
        in: query
        type: string
        format: date-time
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 20
    responses:
      200:
        description: List of event logs
        schema:
          type: object
          properties:
            logs:
              type: array
              items:
                $ref: "#/definitions/EventLog"
            pagination:
              type: object
              properties:
                page:
                  type: integer
                per_page:
                  type: integer
                total:
                  type: integer
                pages:
                  type: integer
    """
    # Parse query parameters
    event_type = request.args.get('event_type')
    actuator_id = request.args.get('actuator_id', type=int)
    user_id = request.args.get('user_id', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Parse dates
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    # Get logs
    logs, total, pages = EventLog.get_logs_filtered(
        event_type=event_type,
        actuator_id=actuator_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages
        }
    }), 200


@logs_bp.route('/<int:log_id>', methods=['GET'])
@jwt_required()
def get_log(log_id):
    """
    Get a specific event log.
    
    ---
    tags:
      - Logs
    summary: Get log by ID
    security:
      - Bearer: []
    parameters:
      - name: log_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Log details
        schema:
          type: object
          properties:
            log:
              $ref: "#/definitions/EventLog"
      404:
        description: Log not found
        schema:
          $ref: "#/definitions/Error"
    """
    log = EventLog.query.get(log_id)
    
    if not log:
        return jsonify({'error': 'Log not found'}), 404
    
    return jsonify({'log': log.to_dict()}), 200


@logs_bp.route('/types', methods=['GET'])
@jwt_required()
def get_event_types():
    """
    Get available event types for filtering.
    
    Returns:
        200: List of event types
    """
    return jsonify({
        'event_types': EventLog.VALID_TYPES
    }), 200


@logs_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_logs_summary():
    """
    Get a summary of event logs.
    
    Query Parameters:
        days: Number of days to include (default: 7)
        
    Returns:
        200: Summary statistics
    """
    from app.extensions import db
    from sqlalchemy import func
    
    days = request.args.get('days', 7, type=int)
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = datetime(end_date.year, end_date.month, end_date.day) - __import__('datetime').timedelta(days=days)
    
    # Get counts by type
    type_counts = db.session.query(
        EventLog.event_type,
        func.count(EventLog.id).label('count')
    ).filter(
        EventLog.created_at >= start_date
    ).group_by(EventLog.event_type).all()
    
    # Get total count
    total = db.session.query(func.count(EventLog.id)).filter(
        EventLog.created_at >= start_date
    ).scalar()
    
    # Get most active actuators
    actuator_counts = db.session.query(
        EventLog.actuator_id,
        EventLog.device_name,
        func.count(EventLog.id).label('count')
    ).filter(
        EventLog.created_at >= start_date,
        EventLog.actuator_id.isnot(None)
    ).group_by(EventLog.actuator_id, EventLog.device_name).order_by(
        func.count(EventLog.id).desc()
    ).limit(5).all()
    
    return jsonify({
        'period': {
            'days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'total_events': total,
        'by_type': {t.event_type: t.count for t in type_counts},
        'most_active_actuators': [
            {'actuator_id': a.actuator_id, 'device_name': a.device_name, 'count': a.count}
            for a in actuator_counts
        ]
    }), 200


@logs_bp.route('/chart-data', methods=['GET'])
@jwt_required()
def get_chart_data():
    """
    Get event log data formatted for charts.
    
    Query Parameters:
        days: Number of days to include (default: 7)
        group_by: Grouping (hour, day)
        
    Returns:
        200: Chart data
    """
    from app.extensions import db
    from sqlalchemy import func
    
    days = request.args.get('days', 7, type=int)
    group_by = request.args.get('group_by', 'day')
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - __import__('datetime').timedelta(days=days)
    
    # Determine truncation function based on group_by
    if group_by == 'hour':
        date_trunc = func.date_trunc('hour', EventLog.created_at)
    else:
        date_trunc = func.date_trunc('day', EventLog.created_at)
    
    # Get counts by date and type
    results = db.session.query(
        date_trunc.label('date'),
        EventLog.event_type,
        func.count(EventLog.id).label('count')
    ).filter(
        EventLog.created_at >= start_date
    ).group_by(date_trunc, EventLog.event_type).order_by(date_trunc).all()
    
    # Format data for charts
    chart_data = {}
    for r in results:
        date_str = r.date.isoformat() if r.date else None
        if date_str not in chart_data:
            chart_data[date_str] = {'date': date_str}
        chart_data[date_str][r.event_type] = r.count
    
    return jsonify({
        'data': list(chart_data.values()),
        'period': {
            'days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'group_by': group_by
    }), 200