from app.database import db
from datetime import datetime

class Entity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'government', 'company', 'university', etc.
    official_id = db.Column(db.String(80), unique=True, nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 