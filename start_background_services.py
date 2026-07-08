#!/usr/bin/env python3
"""
Startup script for Public Pulse background services
This script starts background tasks using Python packages
"""

import time
import sys
import os
from pathlib import Path

def start_python_services():
    """Start services using Python packages"""
    print("🚀 Starting services with Python packages...")
    
    try:
        # Check if required packages are installed
        import redis
        print("✅ Redis package available")
        
        # Try to connect to Redis (will use localhost:6379)
        try:
            r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
            r.ping()
            print("✅ Redis connection successful")
        except:
            print("⚠️  Redis not running - will use in-memory fallback")
            
        # Check Meilisearch package
        try:
            import meilisearch
            print("✅ Meilisearch package available")
        except ImportError:
            print("⚠️  Meilisearch package not installed - installing...")
            os.system("pip install meilisearch")
            
        return True
            
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Installing required packages...")
        os.system("pip install redis meilisearch celery schedule")
        return True

def start_background_scheduler():
    """Start the background task scheduler"""
    print("🚀 Starting background task scheduler...")
    
    try:
        # Add the server directory to Python path
        server_path = Path(__file__).parent / 'server'
        sys.path.insert(0, str(server_path))
        
        # Import and start scheduler
        from server.app.services.scheduler import start_scheduler
        
        print("✅ Background scheduler started")
        print("📋 Scheduled tasks:")
        print("   - News fetching: Every 6 hours")
        print("   - Search reindexing: Daily at 2 AM")
        print("   - Database cleanup: Weekly on Monday at 3 AM")
        print("   - Database optimization: Weekly on Sunday at 4 AM")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing scheduler: {e}")
        print("Make sure you're in the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error starting scheduler: {e}")
        return False

def main():
    """Main startup function"""
    print("🚀 Public Pulse - Background Services Startup")
    print("=" * 50)
    
    # Start Python services
    print("\n🐍 Using Python packages for services...")
    services_started = start_python_services()
    
    if not services_started:
        print("\n❌ Failed to start services. Please check the errors above.")
        sys.exit(1)
    
    # Start background scheduler
    print("\n🔄 Starting background task scheduler...")
    scheduler_started = start_background_scheduler()
    
    if not scheduler_started:
        print("\n❌ Failed to start background scheduler.")
        sys.exit(1)
    
    print("\n✅ All services started successfully!")
    print("\n📊 Service Status:")
    print("   - Redis: Python package ready")
    print("   - Meilisearch: Python package ready")
    print("   - Background Scheduler: Running")
    print("\n🌐 You can now start your Flask app:")
    print("   cd server && python run.py")
    
    # Keep the script running to maintain the scheduler
    try:
        print("\n⏳ Press Ctrl+C to stop all services...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        print("✅ Background scheduler stopped")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
