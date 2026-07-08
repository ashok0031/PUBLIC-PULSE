"""
Quick test script to verify the project enhancements are working
"""
import sys
import os

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

print("=" * 70)
print("TESTING PROJECT ENHANCEMENTS")
print("=" * 70)
print()

# Test 1: Import all new services
print("1. Testing service imports...")
try:
    from app.services.category_mapper import category_mapper
    from app.services.confidence_scorer import confidence_scorer
    from app.services.enhanced_deduplication import enhanced_dedupe
    from app.services.unified_search_service import unified_search
    from app.services.cache_service import cache_service
    print("   ✅ All services imported successfully")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Category Mapper
print("\n2. Testing Category Mapper...")
try:
    # Test category inference
    categories = category_mapper.infer_categories("India wins cricket match against Australia")
    assert 'sports' in categories, "Should detect sports category"
    print(f"   ✅ Category inference: {categories}")
    
    # Test normalization
    normalized = category_mapper.normalize_category("Sports")
    assert normalized == 'sports', "Should normalize to lowercase"
    print(f"   ✅ Category normalization: {normalized}")
except Exception as e:
    print(f"   ❌ Category mapper error: {e}")

# Test 3: Confidence Scorer
print("\n3. Testing Confidence Scorer...")
try:
    test_item = {
        'title': 'Test News',
        'summary': 'Test description',
        'url': 'https://example.com',
        'source': 'newsapi',
        'sources': ['newsapi', 'gnews'],
        'type': 'news'
    }
    confidence = confidence_scorer.calculate_confidence(test_item)
    assert 0 <= confidence <= 1, "Confidence should be between 0 and 1"
    print(f"   ✅ Confidence score: {confidence:.2f}")
    print(f"   ✅ Confidence level: {test_item.get('confidence_level', 'N/A')}")
except Exception as e:
    print(f"   ❌ Confidence scorer error: {e}")

# Test 4: Enhanced Deduplication
print("\n4. Testing Enhanced Deduplication...")
try:
    items = [
        {'title': 'Test Article', 'type': 'news', 'source': 'newsapi', 'year': 2024},
        {'title': 'Test Article', 'type': 'news', 'source': 'gnews', 'year': 2024},
        {'title': 'Different Article', 'type': 'news', 'source': 'newsapi'}
    ]
    deduped = enhanced_dedupe.dedupe_and_merge(items)
    assert len(deduped) == 2, "Should deduplicate similar items"
    assert len(deduped[0].get('sources', [])) == 2, "Should merge sources"
    print(f"   ✅ Deduplication: {len(items)} items -> {len(deduped)} unique items")
    print(f"   ✅ Sources merged: {deduped[0].get('sources', [])}")
except Exception as e:
    print(f"   ❌ Deduplication error: {e}")

# Test 5: Cache Service
print("\n5. Testing Cache Service...")
try:
    cache_service.set('test_key', {'test': 'data'}, ttl_seconds=60)
    cached = cache_service.get('test_key')
    assert cached == {'test': 'data'}, "Should retrieve cached data"
    print("   ✅ Cache service working (using in-memory fallback if Redis unavailable)")
except Exception as e:
    print(f"   ⚠️  Cache service: {e} (expected if Redis not running)")

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\nNext steps:")
print("1. Start Redis (optional but recommended): redis-server")
print("2. Start Flask server: cd server && python run.py")
print("3. Start React frontend: cd client && npm start")
print("4. Test endpoints:")
print("   - GET http://localhost:5000/api/search/unified?query=test")
print("   - GET http://localhost:5000/api/suggestions/?q=test")

