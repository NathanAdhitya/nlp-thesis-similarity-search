import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def before_all(context):
    """Setup before all tests"""
    try:
        # Create minimal Flask app for testing
        from flask import Flask
        app = Flask('test_app')
        app.config['TESTING'] = True
        
        # Add mock routes
        @app.route('/programs')
        def programs():
            return {'message': 'success', 'data': {'programs': []}}
            
        @app.route('/search/paper/<query>')
        def search_paper(query):
            return {'message': 'success', 'data': {'topPapers': []}}
            
        @app.route('/search/author/<query>')
        def search_author(query):
            return {'message': 'success', 'data': {'topAuthors': []}}
        
        context.app = app
        context.client = app.test_client()
        
        print("Test environment setup successful")
    except Exception as e:
        print(f"Setup error: {e}")
        raise

def after_all(context):
    """Cleanup after all tests"""
    if hasattr(context, 'app_context'):
        context.app_context.pop()

def before_scenario(context, scenario):
    """Setup before each scenario"""
    context.response = None
    context.response_data = None

def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    pass