#!/usr/bin/env python3
"""Check if test dependencies are properly installed"""

def check_installation():
    try:
        import behave
        print("✅ Behave installed successfully")
        print(f"   Version: {behave.__version__}")
    except ImportError:
        print("❌ Behave not found. Install with: pip install behave")
        return False
    
    try:
        import requests
        print("✅ Requests installed successfully")
    except ImportError:
        print("❌ Requests not found. Install with: pip install requests")
        return False
    
    try:
        import psutil
        print("✅ Psutil installed successfully")
    except ImportError:
        print("❌ Psutil not found. Install with: pip install psutil")
        return False
    
    print("\n🎉 All test dependencies are installed!")
    print("\nYou can now run tests with:")
    print("  python run_tests.py")
    print("  behave")
    return True

if __name__ == "__main__":
    check_installation()