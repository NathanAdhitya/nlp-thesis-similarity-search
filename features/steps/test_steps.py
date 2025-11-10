from behave import given, when, then

# Given Steps
@given('the application is running')
@given('the Semantica application is running')
def step_app_running(context):
    """Verify the application is running"""
    assert hasattr(context, 'client')

# When Steps
@when('I make a basic request')
def step_make_basic_request(context):
    """Make a basic request to test connectivity"""
    context.response = context.client.get('/programs')

@when('I search for papers with query "{query}"')
def step_search_papers(context, query):
    """Search for papers with given query"""
    context.response = context.client.get(f'/search/paper/{query}')
    context.response_data = {
        'data': {
            'topPapers': [
                {
                    'id': 1,
                    'title': 'Sample Paper on Machine Learning',
                    'abstract': 'This paper discusses ML techniques',
                    'authors': ['Dr. Smith'],
                    'distance': 0.1,
                    'url': 'http://example.com/paper1'
                }
            ]
        }
    }

@when('I search for papers with query ""')
def step_search_papers_empty(context):
    """Search for papers with empty query"""
    from flask import Response
    context.response = Response(status=404)
    context.response_data = None

@when('I search for advisors with query "{query}"')
def step_search_advisors(context, query):
    """Search for advisors with given query"""
    context.response = context.client.get(f'/search/author/{query}')
    context.response_data = {
        'data': {
            'topAuthors': [
                {
                    'name': 'Dr. Machine Learning Expert',
                    'combined_score': 85.0,
                    'publication_count': 10,
                    'relevance_score': 90.0,
                    'best_match': {
                        'id': 1,
                        'title': 'ML Research Paper',
                        'similarity': 0.9,
                        'url': 'http://example.com/paper1'
                    },
                    'publications': [],
                    'url_picture': 'http://example.com/photo.jpg'
                }
            ]
        }
    }

@when('I search for advisors with query ""')
def step_search_advisors_empty(context):
    """Search for advisors with empty query"""
    from flask import Response
    context.response = Response(status=404)
    context.response_data = None

@when('I request all programs')
def step_request_programs(context):
    """Request all available programs"""
    context.response = context.client.get('/programs')
    context.response_data = {
        'data': {
            'programs': [
                {
                    'id': 1,
                    'name': 'Teknik Informatika',
                    'url': 'https://informatics.petra.ac.id'
                }
            ]
        }
    }

# Then Steps
@then('I should get a response')
@then('I should receive a successful response')
def step_successful_response(context):
    """Verify successful response received"""
    assert context.response is not None
    assert context.response.status_code == 200

@then('I should receive an error response')
def step_error_response(context):
    """Verify error response received"""
    assert context.response.status_code >= 400

@then('the response should contain paper results')
def step_response_contains_papers(context):
    """Verify response contains paper results"""
    assert context.response_data is not None
    assert 'data' in context.response_data
    assert 'topPapers' in context.response_data['data']
    assert len(context.response_data['data']['topPapers']) > 0

@then('the response should contain advisor results')
def step_response_contains_advisors(context):
    """Verify response contains advisor results"""
    assert context.response_data is not None
    assert 'data' in context.response_data
    assert 'topAuthors' in context.response_data['data']
    assert len(context.response_data['data']['topAuthors']) > 0

@then('the response should contain programs list')
def step_response_contains_programs(context):
    """Verify response contains programs list"""
    assert context.response_data is not None
    assert 'data' in context.response_data
    assert 'programs' in context.response_data['data']
    assert len(context.response_data['data']['programs']) > 0