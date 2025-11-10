import os
import sys
from flask import Flask

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def before_all(context):
    """Setup before all tests - Test Fixture"""
    # Create simple Flask app for testing
    app = Flask('semantica_test')
    app.config['TESTING'] = True
    
    # Add mock routes for testing
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

def after_all(context):
    """Cleanup after all tests - Test Fixture"""
    pass

def before_scenario(context, scenario):
    """Setup before each scenario - Test Fixture"""
    context.response = None
    context.response_data = None

def after_scenario(context, scenario):
    """Cleanup after each scenario - Test Fixture"""
    pass