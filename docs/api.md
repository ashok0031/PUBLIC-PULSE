# Public Pulse API Documentation

## Auth
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (username/email/phone)

## News
- `GET /api/news` - Get trending news (all categories)
- `GET /api/news/<category>` - Get news by category

## Entities
- `GET /api/entities` - List all registered entities
- `GET /api/entities/<id>` - Get entity details

## Reviews
- `GET /api/reviews/<entity_id>` - Get reviews for entity
- `POST /api/reviews/<entity_id>` - Post a review (auth required)

## Ratings
- `GET /api/ratings/<entity_id>` - Get current rating/trend 