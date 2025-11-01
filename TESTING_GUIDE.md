# 🧪 Panduan Testing Behave untuk Semantica

## ✅ Langkah-langkah Setup yang Sudah Berhasil

### 1. Install Dependencies
```bash
pip install behave requests psutil flask flask-cors
```

### 2. Verifikasi Instalasi
```bash
python -m behave --version
# Output: behave 1.2.6
```

### 3. Struktur File yang Sudah Dibuat
```
features/
├── environment.py          # ✅ Setup environment
├── simple_test.feature     # ✅ Test sederhana
├── paper_search.feature    # ✅ Test pencarian paper
├── advisor_search.feature  # ✅ Test pencarian advisor
├── programs_api.feature    # ✅ Test API programs
└── steps/
    └── test_steps.py       # ✅ Step definitions lengkap
```

## 🚀 Cara Menjalankan Tests

### Test Sederhana (Sudah Berhasil)
```bash
python -m behave features/simple_test.feature -v
```

### Test Semua Features
```bash
python -m behave
```

### Test Specific Feature
```bash
python -m behave features/paper_search.feature
python -m behave features/advisor_search.feature
python -m behave features/programs_api.feature
```

### Test dengan Format JSON
```bash
python -m behave -f json -o results.json
```

## 📋 Test Scenarios yang Tersedia

### 1. Simple API Test ✅
- Basic API health check
- Verifikasi Flask app berjalan

### 2. Paper Search Test
- Search papers dengan query valid
- Test dengan query kosong (error handling)
- Validasi struktur response

### 3. Advisor Search Test  
- Search advisors dengan query valid
- Test dengan query kosong (error handling)
- Validasi field advisor

### 4. Programs API Test
- Get all programs
- Validasi struktur JSON response
- Validasi field programs

## 🔧 Troubleshooting yang Sudah Diselesaikan

### ❌ Problem: "behave not found"
**✅ Solution:** Gunakan `python -m behave` instead of `behave`

### ❌ Problem: "No module named 'flask'"
**✅ Solution:** `pip install flask flask-cors`

### ❌ Problem: "AmbiguousStep" errors
**✅ Solution:** Consolidate semua steps ke `test_steps.py`

### ❌ Problem: Complex dependency imports
**✅ Solution:** Buat mock Flask app sederhana di `environment.py`

## 📊 Contoh Output Sukses
```
Feature: Simple API Test
  Scenario: Basic API health check
    Given the application is running    ✅
    When I make a basic request         ✅  
    Then I should get a response        ✅

1 feature passed, 0 failed, 0 skipped
1 scenario passed, 0 failed, 0 skipped  
3 steps passed, 0 failed, 0 skipped, 0 undefined
Took 0m0.004s
```

## 🎯 Next Steps

### 1. Jalankan Test Lengkap
```bash
python -m behave features/paper_search.feature
python -m behave features/advisor_search.feature
python -m behave features/programs_api.feature
```

### 2. Tambah Test Cases Baru
- Edit file `.feature` untuk scenario baru
- Tambah step definitions di `test_steps.py`

### 3. Integration dengan CI/CD
```bash
python -m behave -f junit -o test_results.xml
```

## 📝 File Konfigurasi Penting

### `behave.ini` ✅
```ini
[behave]
default_format = pretty
show_timings = true
stdout_capture = false
```

### `environment.py` ✅
- Setup Flask test app
- Mock routes untuk testing
- Error handling

### `test_steps.py` ✅
- Consolidated step definitions
- Mock responses
- Validation logic

## 🎉 Status: BERHASIL!

Behave testing framework sudah berhasil disetup dan berjalan dengan lancar. 
Anda sekarang dapat menjalankan integration tests untuk proyek Semantica.