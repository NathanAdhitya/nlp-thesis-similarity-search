# Semantica Integration Testing dengan Behave

## Overview

Proyek ini menggunakan **Behave** (Behavior Driven Development framework) untuk integration testing pada aplikasi Semantica. Testing ini mencakup pengujian API endpoints, fungsionalitas pencarian, dan performa sistem.

## Struktur Testing

```
features/
├── environment.py              # Konfigurasi environment testing
├── paper_search.feature        # Test pencarian paper/tesis
├── advisor_search.feature      # Test pencarian dosen pembimbing
├── programs_api.feature        # Test API programs
├── api_integration.feature     # Test integrasi API dan error handling
├── performance_testing.feature # Test performa dan load testing
└── steps/
    ├── common_steps.py         # Step definitions umum
    ├── paper_search_steps.py   # Step definitions pencarian paper
    ├── advisor_search_steps.py # Step definitions pencarian advisor
    ├── programs_steps.py       # Step definitions API programs
    └── performance_steps.py    # Step definitions performance testing
```

## Fitur Testing

### 1. Paper Search Testing (`paper_search.feature`)
- ✅ Pencarian paper dengan query valid
- ✅ Penggunaan model embedding berbeda (BGE-M3, MiniLM, IndoBERT)
- ✅ Parameter top-k custom
- ✅ Handling query kosong
- ✅ Handling model tidak valid

### 2. Advisor Search Testing (`advisor_search.feature`)
- ✅ Pencarian dosen dengan query valid
- ✅ Filter berdasarkan program studi
- ✅ Penggunaan model embedding berbeda
- ✅ Parameter top-k custom
- ✅ Handling query kosong

### 3. Programs API Testing (`programs_api.feature`)
- ✅ Mengambil daftar semua program
- ✅ Validasi struktur response JSON
- ✅ Validasi field yang diperlukan (id, name, url)

### 4. API Integration Testing (`api_integration.feature`)
- ✅ Validasi CORS headers
- ✅ Handling endpoint tidak valid (404)
- ✅ Handling special characters dalam query
- ✅ Handling query yang sangat panjang
- ✅ Concurrent request handling

### 5. Performance Testing (`performance_testing.feature`)
- ✅ Validasi response time
- ✅ Monitoring penggunaan memory
- ✅ Load testing dengan multiple users
- ✅ Deteksi memory leaks

## Instalasi dan Setup

### 1. Install Dependencies

```bash
# Install test dependencies
pip install -r test_requirements.txt

# Atau install manual
pip install behave==1.2.6 requests==2.31.0 pytest==7.4.3 pytest-mock==3.12.0 psutil
```

### 2. Struktur Project
Pastikan struktur project sesuai dengan yang diharapkan:
```
nlp-thesis-similarity-search/
├── app.py                 # Flask application
├── script.py             # Search engine wrapper
├── main/main/search_engine.py  # Core search engine
├── features/             # Behave test files
└── test_requirements.txt # Test dependencies
```

## Menjalankan Tests

### 1. Menggunakan Test Runner Script

```bash
# Jalankan semua tests
python run_tests.py

# Install dependencies dan jalankan tests
python run_tests.py --install-deps

# Jalankan tests dengan format JSON output
python run_tests.py --format json --output results.json

# Jalankan tests dengan format JUnit (untuk CI/CD)
python run_tests.py --format junit --output test_results.xml

# Jalankan hanya performance tests
python run_tests.py --tags @performance
```

### 2. Menggunakan Behave Langsung

```bash
# Jalankan semua tests
behave

# Jalankan dengan format verbose
behave -f pretty

# Jalankan tests tertentu berdasarkan tag
behave --tags @performance

# Jalankan dengan output JSON
behave -f json -o results.json

# Jalankan feature tertentu
behave features/paper_search.feature
```

### 3. Opsi Testing Lanjutan

```bash
# Jalankan dengan logging detail
behave --logging-level=DEBUG

# Skip tests yang gagal dan lanjutkan
behave --stop

# Jalankan dengan dry-run (tidak execute, hanya validasi)
behave --dry-run
```

## Konfigurasi Testing

### Environment Configuration (`features/environment.py`)
- Setup Flask test client
- Konfigurasi mock database
- Cleanup setelah testing

### Behave Configuration (`behave.ini`)
```ini
[behave]
default_format = pretty
show_timings = true
stdout_capture = false
stderr_capture = false
```

## Mocking Strategy

Testing menggunakan `unittest.mock` untuk:
- **Search Engine**: Mock `script.search()` dan `script.get_all_programs()`
- **Database**: Mock database connections untuk testing terisolasi
- **External APIs**: Mock Google Translator dan model embeddings

### Contoh Mock Response:
```python
# Paper search mock
mock_search.return_value = [
    {
        'id': 1,
        'title': 'Sample Paper on Machine Learning',
        'abstract': 'This paper discusses...',
        'authors': ['Dr. Smith'],
        'distance': 0.1,
        'url': 'http://example.com/paper1'
    }
]
```

## Validasi Testing

### 1. Response Structure Validation
- ✅ Status code validation (200, 404, 500)
- ✅ JSON structure validation
- ✅ Required fields validation
- ✅ Data type validation

### 2. Business Logic Validation
- ✅ Search results relevance
- ✅ Ranking algorithm correctness
- ✅ Filter functionality
- ✅ Parameter handling

### 3. Performance Validation
- ✅ Response time < 5 seconds
- ✅ Memory usage stability
- ✅ Concurrent request handling
- ✅ No memory leaks

## CI/CD Integration

### GitHub Actions Example:
```yaml
name: Integration Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r test_requirements.txt
    - name: Run integration tests
      run: python run_tests.py --format junit --output test_results.xml
    - name: Publish test results
      uses: EnricoMi/publish-unit-test-result-action@v1
      with:
        files: test_results.xml
```

## Troubleshooting

### Common Issues:

1. **Import Errors**
   ```bash
   # Pastikan PYTHONPATH benar
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Database Connection Errors**
   - Tests menggunakan mock, tidak memerlukan database aktual
   - Pastikan mock setup benar di `environment.py`

3. **Model Loading Errors**
   - Tests menggunakan mock untuk model embeddings
   - Tidak memerlukan model aktual untuk testing

4. **Performance Test Failures**
   - Adjust timeout values di `performance_steps.py`
   - Pastikan sistem tidak overloaded saat testing

## Reporting

### Test Reports
- **Pretty Format**: Output console yang readable
- **JSON Format**: Untuk parsing programmatic
- **JUnit Format**: Untuk CI/CD integration

### Coverage Analysis
```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run -m behave
coverage report
coverage html  # Generate HTML report
```

## Best Practices

1. **Test Isolation**: Setiap test independent dan tidak bergantung pada test lain
2. **Mock Usage**: Gunakan mock untuk external dependencies
3. **Clear Assertions**: Assertion yang jelas dan informatif
4. **Performance Monitoring**: Monitor response time dan memory usage
5. **Error Scenarios**: Test berbagai error scenarios dan edge cases

## Kontribusi

Untuk menambah test cases baru:

1. Buat feature file baru di `features/`
2. Implementasi step definitions di `features/steps/`
3. Update dokumentasi ini
4. Jalankan tests untuk memastikan tidak ada regression

## Referensi

- [Behave Documentation](https://behave.readthedocs.io/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.0.x/testing/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)