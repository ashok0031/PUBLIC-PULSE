from app.database import db
from datetime import datetime

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entity_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=True)  # e.g., 'positive', 'negative', 'neutral'
    rating = db.Column(db.Float, nullable=True)  # 1-5 scale or None
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    entity = db.relationship('Entity', backref=db.backref('reviews', lazy=True)) 