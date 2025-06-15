# Semantica: Sistem Paper Semantic Search untuk Dosen Pembimbing Skripsi
## C14220235 Veleroy Juan Andika
## _________ Richard Kamitono
## _________ Nathan Aditya
## _________ Regent Wibisono

## 1. Deskripsi Umum

Semantica adalah aplikasi pencarian semantik yang membantu mahasiswa menemukan dosen pembimbing tesis yang paling sesuai dengan topik penelitian mereka. Sistem ini memanfaatkan teknologi embedding vektor dan database dengan kemampuan pencarian vektor untuk memberikan rekomendasi dosen berdasarkan kesamaan semantik topik penelitian dengan publikasi akademis dosen.

## 2. Teknologi dan Metode

### 2.1 Model Embedding

| Model | Deskripsi | Implementasi |
|-------|-----------|--------------|
| BGE-M3 | BAAI General Embedding Model versi 3 | FlagEmbedding |
| all-MiniLM-L6-v2 | Model embedding ringan | SentenceTransformers |
| IndoBERT | Model BERT fine-tuned untuk bahasa Indonesia | SentenceTransformers |

### 2.2 Database dan Pencarian Vektor

* **SQLite** dengan ekstensi **sqlite_vec**
* Menggunakan teknik KNN (K-Nearest Neighbors) untuk mencari vektor terdekat
* Kueri vektor diimplementasikan menggunakan sintaks SQL dengan klausa `MATCH`

### 2.3 Algoritma Peringkat Dosen

Semantica menawarkan tiga strategi peringkat dosen:

1. **Berbasis Frekuensi**
   * Memprioritaskan dosen dengan lebih banyak publikasi yang sesuai dengan topik
   * Menghitung rata-rata jarak semantik

2. **Berbasis Semantik Murni**
   * Memprioritaskan kesamaan semantik publikasi dengan query
   * Mengkonversi jarak menjadi skor similaritas: `1.0 / (distance + epsilon)`

3. **Pendekatan Hybrid**
   * Menggabungkan jumlah publikasi dan relevansi semantik
   * Bobot yang dapat disesuaikan antara kedua faktor
   * Formula: `(normalized_count × count_weight) + (normalized_similarity × similarity_weight)`

## 3. Arsitektur Sistem

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Svelte UI    │────>│  Flask API    │────>│ SearchEngine  │
│  (Carbon)     │<────│  Endpoints    │<────│    Class      │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                   │
┌───────────────┐     ┌───────────────┐     ┌──────┴────────┐
│  Model        │<────┤  SQLite +     │<────┤ Vector Search │
│  Embeddings   │────>│  sqlite_vec   │────>│    Logic      │
└───────────────┘     └───────────────┘     └───────────────┘
```

## 4. Skema Database

### 4.1 Tabel Utama

| Tabel | Deskripsi |
|-------|-----------|
| publications | Publikasi akademis (judul, abstrak, URL) |
| users | Informasi dosen (nama, minat, foto) |
| programs | Program studi |
| publication_user_mapping | Relasi penulis-publikasi |
| program_user | Relasi program studi-dosen |

### 4.2 Tabel Vektor

| Tabel | Deskripsi |
|-------|-----------|
| publications_vec_bge_m3 | Vektor BGE-M3 untuk publikasi |
| publications_vec_all_MiniLM_L6_v2 | Vektor MiniLM untuk publikasi |
| publications_vec_indobert | Vektor IndoBERT untuk publikasi |

## 5. Alur Kerja Sistem

### 5.1 Pencarian Tesis/Paper

1. Pengguna memasukkan query penelitian
2. Query diubah menjadi vektor embedding
3. Sistem mencari publikasi dengan vektor terdekat
4. Hasil diurutkan berdasarkan jarak semantik

### 5.2 Pencarian Dosen Pembimbing

1. Pengguna memasukkan topik penelitian
2. Sistem mencari publikasi yang relevan
3. Penulis publikasi dikelompokkan dan diperingkat
4. Hasil diurutkan berdasarkan algoritma peringkat yang dipilih
5. Detail dosen dan publikasi terkait ditampilkan

### 5.3 Fitur Filter

* Filter berdasarkan program studi
* Pemilihan model embedding
* Pengaturan jumlah hasil (Top-K)

## 6. API Endpoints

| Endpoint | Metode | Deskripsi |
|----------|--------|-----------|
| /search/paper/{query} | GET | Mencari paper/tesis berdasarkan query |
| /search/author/{query} | GET | Mencari dosen berdasarkan topik |
| /programs | GET | Mendapatkan daftar program studi |

## 7. Optimisasi Kinerja

* Multithreading untuk memuat model secara paralel
* Pemilihan model embedding berdasarkan kebutuhan
* Kueri SQL yang dioptimalkan untuk pengambilan data

## 8. Fitur Khusus

* Dukungan bahasa ganda melalui Google Translator
* Normalisasi skor untuk perbandingan yang adil
* Custom photo profiling untuk dosen tertentu
* Kombinasi peringkat berbasis semantik dan kuantitas

## 9. Antarmuka Pengguna

Antarmuka pengguna Semantica dibangun menggunakan Svelte dengan komponen Carbon dari IBM, menawarkan:

* Bilah pencarian untuk input query
* ContentSwitcher untuk memilih antara pencarian paper dan dosen
* Filter untuk program studi (khusus pencarian dosen)
* Pengaturan model dan parameter Top-K
* ExpandableTile untuk menampilkan hasil pencarian dengan detail
* Pagination untuk navigasi hasil
* Modal untuk pengaturan pencarian

## 10. Pengembangan Masa Depan

* Integrasi model embedding tambahan
* Peningkatan algoritma peringkat
* Fitur personalisasi untuk preferensi pengguna
* Analisis sentimen untuk evaluasi publikasi
* Dukungan untuk domain keilmuan khusus
