#!/usr/bin/env python3
"""Quick test to verify setup works"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_test():
    try:
        from app import app
        
        # Test Flask app
        app.config['TESTING'] = True
        client = app.test_client()
        
        print("Testing Flask app...")
        response = client.get('/programs')
        print(f"Programs endpoint status: {response.status_code}")
        
        print("✅ Basic setup working!")
        print("\nNow install behave and run full tests:")
        print("  pip install behave")
        print("  python run_tests.py")
        
    except Exception as e:
        print(f"❌ Setup issue: {e}")
        print("Make sure you're in the correct directory and dependencies are installed")

if __name__ == "__main__":
    quick_test()