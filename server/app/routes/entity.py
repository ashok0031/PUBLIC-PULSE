from flask import Blueprint, jsonify
from app.models.entity import Entity

entity_bp = Blueprint('entity', __name__, url_prefix='/api/entities')

@entity_bp.route('/', methods=['GET'])
def list_entities():
    entities = Entity.query.all()
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'type': e.type,
        'official_id': e.official_id,
        'logo_url': e.logo_url,
        'description': e.description
    } for e in entities])

@entity_bp.route('/<int:entity_id>', methods=['GET'])
def get_entity(entity_id):
    entity = Entity.query.get_or_404(entity_id)
    return jsonify({
        'id': entity.id,
        'name': entity.name,
        'type': entity.type,
        'official_id': entity.official_id,
        'logo_url': entity.logo_url,
        'description': entity.description
    }) 