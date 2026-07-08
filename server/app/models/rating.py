from app.database import db
from datetime import datetime

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entity.id'), unique=True, nullable=False)
    average_rating = db.Column(db.Float, nullable=True)
    trend_data = db.Column(db.JSON, nullable=True)  # e.g., {"2024-06-01": 4.2, ...}
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    entity = db.relationship('Entity', backref=db.backref('rating', uselist=False)) 