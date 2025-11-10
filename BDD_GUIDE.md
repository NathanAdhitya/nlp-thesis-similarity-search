# Behavior Driven Development (BDD) dengan Behave

## Konsep BDD

**BDD adalah test-first approach yang menguji behavior sistem dari luar ke dalam:**
- BDD melihat sistem dari perspektif user
- BDD tidak tertarik dengan inner workings sistem
- BDD menggunakan syntax yang dipahami developer dan stakeholder

## Struktur Testing

```
Acceptance Testing
    ↓
System / End-to-end Testing  
    ↓
Integration Testing ← (Kita di sini)
    ↓
Unit Testing
```

## BDD Workflow

1. **Kolaborasi** antara stakeholder untuk menghasilkan contoh konkret
2. **Gunakan BDD tools** untuk menjalankan contoh sebagai automated tests
3. **Tools menunjukkan** contoh mana yang sudah diimplementasi dan bekerja
4. **Hasil akhir:** satu dokumen yang bertindak sebagai spesifikasi dan test

## Gherkin Syntax

### Feature Structure
```gherkin
Feature: <title>

As a <role>
I want <functionality>
So that <benefit>

Background:
  Given <initial state>

Scenario: <scenario name>
  Given <precondition>
  When <action>
  Then <expected result>
```

### Contoh Feature File
```gherkin
Feature: Paper Search Functionality
  As a student
  I want to search for academic papers
  So that I can find relevant research for my thesis

  Background:
    Given the Semantica application is running

  Scenario: Search for papers with valid query
    When I search for papers with query "machine learning"
    Then I should receive a successful response
    And the response should contain paper results
```

## Behave Framework

**Behave adalah framework untuk BDD di Python:**
- Membaca feature files
- Mencari matching steps
- Mengeksekusi fungsi-fungsi tersebut

### Step Definitions

```python
from behave import given, when, then

@given('the Semantica application is running')
def step_app_running(context):
    assert hasattr(context, 'client')

@when('I search for papers with query "{query}"')
def step_search_papers(context, query):
    context.response = context.client.get(f'/search/paper/{query}')

@then('I should receive a successful response')
def step_successful_response(context):
    assert context.response.status_code == 200
```

## Variable Substitutions

**Rules untuk variables:**
- Gunakan `{}` untuk menandai variable
- Tambahkan `variable_name` ke function sebagai parameter

```gherkin
When I search for papers with query "{query}"
```

```python
@when('I search for papers with query "{query}"')
def step_search_papers(context, query):
    # query adalah parameter yang disubstitusi
    context.response = context.client.get(f'/search/paper/{query}')
```

## Context Variable

**Context adalah variable khusus yang:**
- Diteruskan ke setiap step definition dan fixture
- Tersedia untuk seluruh feature file
- Berguna untuk passing informasi antar steps

```python
@when('I search for papers with query "{query}"')
def step_search_papers(context, query):
    context.response = context.client.get(f'/search/paper/{query}')
    context.query_used = query

@then('I should receive a successful response')
def step_successful_response(context):
    assert context.response.status_code == 200
    # context.query_used masih tersedia di sini
```

## Test Fixtures (Environment Setup)

**Behave memiliki test fixtures yang dapat dieksekusi:**
- `before_all` / `after_all` - Sebelum/sesudah semua testing
- `before_feature` / `after_feature` - Sebelum/sesudah features
- `before_scenario` / `after_scenario` - Sebelum/sesudah scenarios
- `before_step` / `after_step` - Sebelum/sesudah steps

```python
def before_all(context):
    """Setup sebelum semua tests"""
    context.app = create_test_app()
    context.client = context.app.test_client()

def before_scenario(context, scenario):
    """Setup sebelum setiap scenario"""
    context.response = None
```

## Menjalankan Tests

```bash
# Jalankan semua tests
behave

# Jalankan feature tertentu
behave features/paper_search.feature

# Jalankan dengan verbose output
behave -v

# Jalankan scenario tertentu
behave -n "Search for papers with valid query"
```

## File Structure Project

```
features/
├── environment.py          # Test fixtures
├── paper_search.feature    # Feature untuk pencarian paper
├── advisor_search.feature  # Feature untuk pencarian advisor
├── programs_api.feature    # Feature untuk API programs
├── simple_test.feature     # Feature test sederhana
└── steps/
    └── test_steps.py       # Step definitions
```

## Best Practices

1. **Feature Writing:**
   - Konsisten dalam penulisan
   - Pertimbangkan user experience/perspective
   - Build in cues bahwa sistem sudah merespons dengan benar

2. **Step Definitions:**
   - Tulis steps untuk setiap gherkin scenario
   - Gunakan decorators: `@given`, `@when`, `@then`
   - Manfaatkan variable substitutions untuk reusability

3. **Test Data:**
   - Gunakan Background section untuk initial state
   - Manfaatkan context untuk sharing data antar steps