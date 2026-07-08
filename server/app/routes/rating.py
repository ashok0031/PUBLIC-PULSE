from flask import Blueprint, jsonify
from app.models.rating import Rating

rating_bp = Blueprint('rating', __name__, url_prefix='/api/ratings')

@rating_bp.route('/<int:entity_id>', methods=['GET'])
def get_rating(entity_id):
    rating = Rating.query.filter_by(entity_id=entity_id).first()
    if not rating:
        return jsonify({'error': 'No rating found'}), 404
    return jsonify({
        'entity_id': rating.entity_id,
        'average_rating': rating.average_rating,
        'trend_data': rating.trend_data,
        'updated_at': rating.updated_at.isoformat()
    }) 