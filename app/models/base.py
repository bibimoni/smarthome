"""Base model with common fields."""
from datetime import datetime
from app import db


class BaseModel(db.Model):
    """Abstract base model with common fields."""
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Save the model to the database."""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """Delete the model from the database."""
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Convert model to dictionary. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement to_dict()")