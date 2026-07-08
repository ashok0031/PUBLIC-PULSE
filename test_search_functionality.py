"""
Test script to verify search functionality for companies, sports, and movies
Run this after starting your Flask server (python run.py)
"""
import requests
import json
import time

API_BASE = "http://localhost:5000/api"

def test_search(query, expected_type):
    """Test a search query and verify it returns the expected entity type"""
    print(f"\n{'='*60}")
    print(f"Testing: {query} (Expected: {expected_type})")
    print(f"{'='*60}")
    
    # Test unified search
    url = f"{API_BASE}/search/unified?query={query}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
        
        data = response.json()
        
        # Check for entity cards
        companies = data.get('companies', [])
        sports = data.get('sports', [])
        movies = data.get('movies', [])
        gov_schemes = data.get('gov_schemes', [])
        
        print(f"✅ Search successful")
        print(f"   Companies found: {len(companies)}")
        print(f"   Sports found: {len(sports)}")
        print(f"   Movies found: {len(movies)}")
        print(f"   Gov schemes found: {len(gov_schemes)}")
        
        # Check if expected type has results
        has_expected = False
        if expected_type == 'company' and companies:
            has_expected = True
            entity = companies[0]
        elif expected_type == 'sports' and sports:
            has_expected = True
            entity = sports[0]
        elif expected_type == 'movie' and movies:
            has_expected = True
            entity = movies[0]
        elif expected_type == 'gov_scheme' and gov_schemes:
            has_expected = True
            entity = gov_schemes[0]
        
        if has_expected:
            print(f"✅ Found {expected_type} entity!")
            print(f"   Title: {entity.get('title', 'N/A')}")
            print(f"   Type: {entity.get('type', 'N/A')}")
            print(f"   Has image: {bool(entity.get('image'))}")
            print(f"   Has description: {bool(entity.get('description') or entity.get('summary'))}")
            
            # Test rating fetch
            entity_title = entity.get('title', query)
            rating_url = f"{API_BASE}/reviews/aggregate?query={entity_title}"
            try:
                rating_response = requests.get(rating_url, timeout=30)
                if rating_response.status_code == 200:
                    rating_data = rating_response.json()
                    rating = rating_data.get('public_pulse_rating', 'N/A')
                    print(f"   PP Rating: {rating}")
                    if rating != 'N/A' and rating is not None:
                        print(f"✅ Rating fetched successfully!")
                    else:
                        print(f"⚠️  Rating is N/A (may need more reviews)")
                else:
                    print(f"⚠️  Rating fetch failed: {rating_response.status_code}")
            except Exception as e:
                print(f"⚠️  Rating fetch error: {e}")
            
            return True
        else:
            print(f"❌ No {expected_type} entity found!")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server. Make sure Flask server is running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("="*60)
    print("SEARCH FUNCTIONALITY TEST")
    print("="*60)
    print("\nMake sure your Flask server is running (python run.py)")
    print("Press Ctrl+C to cancel, or wait 5 seconds to start...")
    time.sleep(5)
    
    tests = [
        ("Tesla", "company"),
        ("Mumbai Indians", "sports"),
        ("Inception", "movie"),
        ("TATA", "company"),
        ("Chennai Super Kings", "sports"),
    ]
    
    results = []
    for query, expected_type in tests:
        result = test_search(query, expected_type)
        results.append((query, expected_type, result))
        time.sleep(2)  # Small delay between requests
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for _, _, r in results if r)
    total = len(results)
    
    for query, expected_type, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {query} ({expected_type})")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Search functionality is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()

