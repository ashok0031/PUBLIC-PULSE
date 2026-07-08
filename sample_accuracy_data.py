# Sample Search Accuracy Data for Public Pulse Project
# This file contains realistic sample data that matches the existing codebase structure

import json
from datetime import datetime, timedelta
import random

# Sample accuracy data for 5 different searches matching your existing categories
SAMPLE_SEARCH_ACCURACY_DATA = [
    {
        "search_query": "Tesla Motors",
        "search_category": "company",
        "user_id": 1,
        "accuracy_rating": 4.2,
        "relevance_score": 0.85,
        "completeness_score": 0.78,
        "freshness_score": 0.82,
        "results_count": 12,
        "clicked_results": [1, 3, 5, 7],
        "time_spent": 45,
        "user_feedback": "Found good company info and recent news",
        "was_helpful": True,
        "created_at": "2024-01-15T10:30:00Z",
        "result_types": {
            "company": {
                "title": "Tesla, Inc.",
                "description": "American electric vehicle and clean energy company",
                "accuracy": 4.5,
                "found": True
            },
            "news": [
                {
                    "title": "Tesla Reports Record Q4 Deliveries",
                    "source": "Reuters",
                    "accuracy": 4.0,
                    "clicked": True
                },
                {
                    "title": "Tesla Stock Price Analysis",
                    "source": "Bloomberg",
                    "accuracy": 3.8,
                    "clicked": True
                }
            ],
            "images": 3,
            "web": 5
        }
    },
    {
        "search_query": "Inception movie",
        "search_category": "movie",
        "user_id": 2,
        "accuracy_rating": 4.7,
        "relevance_score": 0.92,
        "completeness_score": 0.88,
        "freshness_score": 0.75,
        "results_count": 8,
        "clicked_results": [1, 2, 4],
        "time_spent": 32,
        "user_feedback": "Perfect movie information with cast details",
        "was_helpful": True,
        "created_at": "2024-01-16T14:20:00Z",
        "result_types": {
            "movie": {
                "title": "Inception",
                "description": "2010 science fiction action film directed by Christopher Nolan",
                "accuracy": 4.8,
                "found": True,
                "cast": "Leonardo DiCaprio, Marion Cotillard, Tom Hardy"
            },
            "news": [
                {
                    "title": "Inception 10th Anniversary Celebration",
                    "source": "Variety",
                    "accuracy": 4.2,
                    "clicked": False
                }
            ],
            "images": 4,
            "web": 3
        }
    },
    {
        "search_query": "PM Kisan Yojana",
        "search_category": "government schemes",
        "user_id": 3,
        "accuracy_rating": 4.1,
        "relevance_score": 0.89,
        "completeness_score": 0.82,
        "freshness_score": 0.85,
        "results_count": 15,
        "clicked_results": [1, 2, 3, 6, 8],
        "time_spent": 67,
        "user_feedback": "Comprehensive information about the scheme",
        "was_helpful": True,
        "created_at": "2024-01-17T09:15:00Z",
        "result_types": {
            "gov_scheme": {
                "title": "Pradhan Mantri Kisan Samman Nidhi",
                "description": "Direct income support scheme for farmers",
                "accuracy": 4.3,
                "found": True
            },
            "news": [
                {
                    "title": "PM Kisan 15th Installment Released",
                    "source": "The Hindu",
                    "accuracy": 4.5,
                    "clicked": True
                },
                {
                    "title": "PM Kisan Scheme Benefits 12 Crore Farmers",
                    "source": "Economic Times",
                    "accuracy": 4.0,
                    "clicked": True
                }
            ],
            "images": 2,
            "web": 8
        }
    },
    {
        "search_query": "Bitcoin price",
        "search_category": "finance",
        "user_id": 4,
        "accuracy_rating": 3.8,
        "relevance_score": 0.76,
        "completeness_score": 0.71,
        "freshness_score": 0.95,
        "results_count": 20,
        "clicked_results": [1, 4, 7, 9, 12],
        "time_spent": 28,
        "user_feedback": "Good current price data but too many ads",
        "was_helpful": True,
        "created_at": "2024-01-18T16:45:00Z",
        "result_types": {
            "finance": {
                "title": "Bitcoin (BTC) Price",
                "description": "Current Bitcoin price and market data",
                "accuracy": 4.0,
                "found": True,
                "current_price": "$42,350"
            },
            "news": [
                {
                    "title": "Bitcoin Surges Past $42K",
                    "source": "CoinDesk",
                    "accuracy": 4.2,
                    "clicked": True
                },
                {
                    "title": "Crypto Market Analysis",
                    "source": "Forbes",
                    "accuracy": 3.5,
                    "clicked": True
                }
            ],
            "images": 1,
            "web": 12
        }
    },
    {
        "search_query": "Mumbai Indians",
        "search_category": "sports",
        "user_id": 5,
        "accuracy_rating": 4.4,
        "relevance_score": 0.87,
        "completeness_score": 0.84,
        "freshness_score": 0.79,
        "results_count": 10,
        "clicked_results": [1, 2, 5],
        "time_spent": 41,
        "user_feedback": "Great team stats and recent match results",
        "was_helpful": True,
        "created_at": "2024-01-19T11:30:00Z",
        "result_types": {
            "sports": {
                "title": "Mumbai Indians",
                "description": "Indian Premier League cricket team",
                "accuracy": 4.6,
                "found": True,
                "league": "IPL",
                "captain": "Rohit Sharma"
            },
            "news": [
                {
                    "title": "MI vs CSK Match Preview",
                    "source": "ESPN Cricinfo",
                    "accuracy": 4.3,
                    "clicked": True
                },
                {
                    "title": "Mumbai Indians Squad Analysis",
                    "source": "Sportskeeda",
                    "accuracy": 4.1,
                    "clicked": False
                }
            ],
            "images": 5,
            "web": 4
        }
    }
]

# Additional sample data for generating trends and graphs
ACCURACY_TREND_DATA = [
    {"date": "2024-01-15", "avg_accuracy": 4.2, "search_count": 1},
    {"date": "2024-01-16", "avg_accuracy": 4.7, "search_count": 1},
    {"date": "2024-01-17", "avg_accuracy": 4.1, "search_count": 1},
    {"date": "2024-01-18", "avg_accuracy": 3.8, "search_count": 1},
    {"date": "2024-01-19", "avg_accuracy": 4.4, "search_count": 1}
]

# Category-wise accuracy breakdown
CATEGORY_ACCURACY_BREAKDOWN = {
    "company": {"avg_accuracy": 4.2, "total_searches": 1, "satisfaction_rate": 0.85},
    "movie": {"avg_accuracy": 4.7, "total_searches": 1, "satisfaction_rate": 0.92},
    "government schemes": {"avg_accuracy": 4.1, "total_searches": 1, "satisfaction_rate": 0.89},
    "finance": {"avg_accuracy": 3.8, "total_searches": 1, "satisfaction_rate": 0.76},
    "sports": {"avg_accuracy": 4.4, "total_searches": 1, "satisfaction_rate": 0.87}
}

# Sample data for accuracy metrics over time
ACCURACY_METRICS_TIMELINE = [
    {
        "timestamp": "2024-01-15T10:30:00Z",
        "search_query": "Tesla Motors",
        "metrics": {
            "relevance_score": 0.85,
            "completeness_score": 0.78,
            "freshness_score": 0.82,
            "overall_accuracy": 4.2
        }
    },
    {
        "timestamp": "2024-01-16T14:20:00Z",
        "search_query": "Inception movie",
        "metrics": {
            "relevance_score": 0.92,
            "completeness_score": 0.88,
            "freshness_score": 0.75,
            "overall_accuracy": 4.7
        }
    },
    {
        "timestamp": "2024-01-17T09:15:00Z",
        "search_query": "PM Kisan Yojana",
        "metrics": {
            "relevance_score": 0.89,
            "completeness_score": 0.82,
            "freshness_score": 0.85,
            "overall_accuracy": 4.1
        }
    },
    {
        "timestamp": "2024-01-18T16:45:00Z",
        "search_query": "Bitcoin price",
        "metrics": {
            "relevance_score": 0.76,
            "completeness_score": 0.71,
            "freshness_score": 0.95,
            "overall_accuracy": 3.8
        }
    },
    {
        "timestamp": "2024-01-19T11:30:00Z",
        "search_query": "Mumbai Indians",
        "metrics": {
            "relevance_score": 0.87,
            "completeness_score": 0.84,
            "freshness_score": 0.79,
            "overall_accuracy": 4.4
        }
    }
]

# Function to generate additional sample data
def generate_additional_sample_data():
    """Generate more sample data for testing and demonstration"""
    additional_searches = []
    
    # Generate data for more searches
    search_queries = [
        "Apple Inc", "Avengers Endgame", "Ayushman Bharat", "Gold prices", "Chennai Super Kings",
        "Microsoft", "The Dark Knight", "Digital India", "Stock market", "Royal Challengers Bangalore",
        "Google", "Interstellar", "Make in India", "Mutual funds", "Delhi Capitals"
    ]
    
    categories = ["company", "movie", "government schemes", "finance", "sports"]
    
    for i, query in enumerate(search_queries):
        category = categories[i % len(categories)]
        base_date = datetime(2024, 1, 15) + timedelta(days=i)
        
        search_data = {
            "search_query": query,
            "search_category": category,
            "user_id": (i % 5) + 1,
            "accuracy_rating": round(random.uniform(3.5, 4.8), 1),
            "relevance_score": round(random.uniform(0.7, 0.95), 2),
            "completeness_score": round(random.uniform(0.65, 0.9), 2),
            "freshness_score": round(random.uniform(0.7, 0.95), 2),
            "results_count": random.randint(5, 25),
            "clicked_results": list(range(1, random.randint(2, 8))),
            "time_spent": random.randint(20, 80),
            "user_feedback": f"Search for {query} was {'helpful' if random.random() > 0.2 else 'not very helpful'}",
            "was_helpful": random.random() > 0.2,
            "created_at": base_date.isoformat() + "Z"
        }
        additional_searches.append(search_data)
    
    return additional_searches

# Export all sample data
SAMPLE_DATA_EXPORT = {
    "search_accuracy_data": SAMPLE_SEARCH_ACCURACY_DATA,
    "accuracy_trend_data": ACCURACY_TREND_DATA,
    "category_accuracy_breakdown": CATEGORY_ACCURACY_BREAKDOWN,
    "accuracy_metrics_timeline": ACCURACY_METRICS_TIMELINE,
    "additional_sample_data": generate_additional_sample_data()
}

if __name__ == "__main__":
    # Save sample data to JSON file
    with open('sample_accuracy_data.json', 'w') as f:
        json.dump(SAMPLE_DATA_EXPORT, f, indent=2)
    
    print("Sample accuracy data generated successfully!")
    print(f"Total searches: {len(SAMPLE_SEARCH_ACCURACY_DATA)}")
    print(f"Categories covered: {list(CATEGORY_ACCURACY_BREAKDOWN.keys())}")
    print(f"Average accuracy: {sum(s['accuracy_rating'] for s in SAMPLE_SEARCH_ACCURACY_DATA) / len(SAMPLE_SEARCH_ACCURACY_DATA):.2f}")
