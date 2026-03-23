"""SensorData and EventLog models for data storage and logging."""
from datetime import datetime, timedelta
from app.extensions import db


class SensorData(db.Model):
    """Sensor data model for storing sensor readings."""
    
    __tablename__ = 'sensor_data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Index for efficient querying
    __table_args__ = (
        db.Index('idx_sensor_data_sensor_recorded', 'sensor_id', 'recorded_at'),
    )
    
    @staticmethod
    def get_aggregated_data(sensor_id: int, interval: str = 'hour', days: int = 7) -> list:
        """
        Get aggregated data for a sensor.
        
        Args:
            sensor_id: The sensor ID
            interval: Aggregation interval ('hour', 'day', 'week')
            days: Number of days to look back
            
        Returns:
            List of aggregated data points
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        data = SensorData.query.filter(
            SensorData.sensor_id == sensor_id,
            SensorData.recorded_at >= start_time,
            SensorData.recorded_at <= end_time
        ).order_by(SensorData.recorded_at.asc()).all()
        
        return data
    
    @staticmethod
    def cleanup_old_data(days: int = 90):
        """
        Remove sensor data older than the specified number of days.
        
        Args:
            days: Number of days to keep (default 90)
            
        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_data = SensorData.query.filter(SensorData.recorded_at < cutoff_date).all()
        count = len(old_data)
        for data in old_data:
            db.session.delete(data)
        db.session.commit()
        return count
    
    def to_dict(self) -> dict:
        """Convert sensor data to dictionary."""
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'value': self.value,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
        }
    
    def __repr__(self):
        return f'<SensorData sensor={self.sensor_id} value={self.value}>'


class EventLog(db.Model):
    """Event log model for tracking system activities."""
    
    __tablename__ = 'event_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type = db.Column(db.String(20), nullable=False, index=True)  # ALERT, AUTO, MANUAL, ERROR
    actuator_id = db.Column(db.Integer, db.ForeignKey('actuators.id', ondelete='SET NULL'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    device_name = db.Column(db.String(100), nullable=True)  # Stored as text for historical record
    description = db.Column(db.Text, nullable=False)
    event_metadata = db.Column(db.JSON, nullable=True)  # Additional event data
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Event type constants
    TYPE_ALERT = 'ALERT'
    TYPE_AUTO = 'AUTO'
    TYPE_MANUAL = 'MANUAL'
    TYPE_ERROR = 'ERROR'
    TYPE_SCENE = 'SCENE'
    
    VALID_TYPES = [TYPE_ALERT, TYPE_AUTO, TYPE_MANUAL, TYPE_ERROR, TYPE_SCENE]
    
    @staticmethod
    def log_event(event_type: str, description: str, actuator_id: int = None, 
                  user_id: int = None, device_name: str = None, metadata: dict = None) -> 'EventLog':
        """
        Create and save a new event log entry.
        
        Args:
            event_type: Type of event (ALERT, AUTO, MANUAL, ERROR, SCENE)
            description: Human-readable description of the event
            actuator_id: Optional actuator ID involved
            user_id: Optional user ID who triggered the event
            device_name: Device name (stored separately for historical record)
            metadata: Optional additional data as JSON
            
        Returns:
            The created EventLog instance
        """
        event = EventLog(
            event_type=event_type,
            description=description,
            actuator_id=actuator_id,
            user_id=user_id,
            device_name=device_name,
            event_metadata=metadata
        )
        db.session.add(event)
        db.session.commit()
        return event
    
    @staticmethod
    def get_logs_filtered(event_type: str = None, actuator_id: int = None,
                          user_id: int = None, start_date: datetime = None,
                          end_date: datetime = None, page: int = 1, per_page: int = 20) -> tuple:
        """
        Get filtered event logs with pagination.
        
        Args:
            event_type: Filter by event type
            actuator_id: Filter by actuator ID
            user_id: Filter by user ID
            start_date: Filter events after this date
            end_date: Filter events before this date
            page: Page number for pagination
            per_page: Number of items per page
            
        Returns:
            Tuple of (logs list, total count, total pages)
        """
        query = EventLog.query
        
        if event_type:
            query = query.filter(EventLog.event_type == event_type)
        if actuator_id:
            query = query.filter(EventLog.actuator_id == actuator_id)
        if user_id:
            query = query.filter(EventLog.user_id == user_id)
        if start_date:
            query = query.filter(EventLog.created_at >= start_date)
        if end_date:
            query = query.filter(EventLog.created_at <= end_date)
        
        query = query.order_by(EventLog.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total, pagination.pages
    
    @staticmethod
    def cleanup_old_logs(days: int = 365):
        """
        Remove event logs older than the specified number of days.
        
        Args:
            days: Number of days to keep (default 365)
            
        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_logs = EventLog.query.filter(EventLog.created_at < cutoff_date).all()
        count = len(old_logs)
        for log in old_logs:
            db.session.delete(log)
        db.session.commit()
        return count
    
    def to_dict(self) -> dict:
        """Convert event log to dictionary."""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'actuator_id': self.actuator_id,
            'user_id': self.user_id,
            'device_name': self.device_name,
            'description': self.description,
            'metadata': self.event_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<EventLog {self.event_type}: {self.description[:50]}>'