#!/usr/bin/env python3
"""
API Testing Script for Public Pulse
This script tests all your API keys to see which ones are working
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('server/.env')

def test_newsdata_api():
    """Test NewsData.io API"""
    api_key = os.getenv('NEWSDATA_API_KEY')
    if not api_key:
        return "❌ No API key found"
    
    try:
        url = f"https://newsdata.io/api/1/latest?apikey={api_key}&country=in&language=en"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return f"✅ Working - {len(data.get('results', []))} articles found"
        else:
            return f"❌ Error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def test_newsapi():
    """Test NewsAPI.org"""
    api_key = os.getenv('NEWSAPI_API_KEY')
    if not api_key:
        return "❌ No API key found"
    
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return f"✅ Working - {data.get('totalResults', 0)} articles found"
        else:
            return f"❌ Error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def test_gnews_api():
    """Test GNews API"""
    api_key = os.getenv('GNEWS_API_KEY')
    if not api_key:
        return "❌ No API key found"
    
    try:
        url = f"https://gnews.io/api/v4/top-headlines?country=in&lang=en&apikey={api_key}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return f"✅ Working - {len(data.get('articles', []))} articles found"
        else:
            return f"❌ Error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def test_gemini_api():
    """Test Google Gemini API"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return "❌ No API key found"
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, test message")
        return f"✅ Working - Response: {response.text[:50]}..."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def main():
    """Test all APIs"""
    print("🔍 Testing API Keys...")
    print("=" * 50)
    
    apis = [
        ("NewsData.io", test_newsdata_api),
        ("NewsAPI.org", test_newsapi),
        ("GNews API", test_gnews_api),
        ("Google Gemini", test_gemini_api),
    ]
    
    for name, test_func in apis:
        print(f"\n📰 {name}:")
        result = test_func()
        print(f"   {result}")
    
    print("\n" + "=" * 50)
    print("✅ API testing complete!")
    print("\n💡 If any APIs show errors, get new keys from the websites above.")

if __name__ == "__main__":
    main()
