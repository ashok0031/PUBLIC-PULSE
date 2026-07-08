from app.database import db, init_db
from app.models import User, Entity, Review, Rating
from flask import Flask
from werkzeug.security import generate_password_hash

app = Flask(__name__)
init_db(app)

with app.app_context():
    db.create_all()
    # Add demo users
    if not User.query.filter_by(username='demo').first():
        user = User(username='demo', email='demo@example.com', phone='1234567890', password_hash=generate_password_hash('password'))
        db.session.add(user)
    # Add demo entity
    if not Entity.query.filter_by(name='Demo University').first():
        entity = Entity(name='Demo University', type='university', official_id='U123', logo_url='', description='A demo university for testing.')
        db.session.add(entity)
    db.session.commit()
    # Add demo review
    user = User.query.filter_by(username='demo').first()
    entity = Entity.query.filter_by(name='Demo University').first()
    if user and entity and not Review.query.filter_by(user_id=user.id, entity_id=entity.id).first():
        review = Review(user_id=user.id, entity_id=entity.id, text='Great place to study!', sentiment='positive', rating=4.5)
        db.session.add(review)
        db.session.commit()
    # Add demo rating
    if entity and not Rating.query.filter_by(entity_id=entity.id).first():
        rating = Rating(entity_id=entity.id, average_rating=4.5, trend_data={"2024-06-01": 4.5})
        db.session.add(rating)
        db.session.commit() 