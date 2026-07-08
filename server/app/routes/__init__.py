from .auth import auth_bp
from .entity import entity_bp
from .review import review_bp
from .rating import rating_bp
from .news import news_bp
from .search import search_bp
from .ai import ai_bp
from .optimized_news import optimized_news_bp
from .suggestions import suggestions_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(entity_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(rating_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(optimized_news_bp)
    app.register_blueprint(suggestions_bp) 