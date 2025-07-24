# LUMIRA Research Assistant - Project Structure

## 📁 File Structure

```
lomba/
├── main.py                    # Script utama research assistant
├── riset_agent.py            # Entry point sederhana dengan default config
├── demo.py                   # Demo mode untuk testing
├── config.json               # Konfigurasi default dan settings
├── requirements.txt          # Dependencies Python
├── README.md                 # Dokumentasi lengkap
├── PROJECT_STRUCTURE.md      # File ini - dokumentasi struktur
└── .venv/                    # Virtual environment Python
```

## 🚀 Cara Penggunaan

### 1. Setup Awal

```bash
# Pastikan di dalam folder lomba
cd /home/david/hackaton/lomba

# Install dependencies (sudah dilakukan)
pip install -r requirements.txt
```

### 2. Jalankan Demo (Recommended)

```bash
python demo.py
```

Output: Folder `Demo_Output` dengan 5 sumber sample

### 3. Jalankan Full Research

```bash
python riset_agent.py
```

Output: Folder `Riset Vokasi Indonesia – LUMIRA` dengan 15 sumber

### 4. Custom Research

```bash
python main.py --topic "SMK digital transformation" --max_sources 20 --summarize --extract_data
```

## 📊 Output Files

### Laporan_Riset_Lengkap.md

- Executive summary penelitian
- Daftar semua sumber dengan scoring
- Ringkasan per sumber dalam Bahasa Indonesia
- Tabel data penting
- Rekomendasi berdasarkan analisis

### Database_Sumber_Riset.xlsx/.csv

- Spreadsheet dengan semua sumber
- Kolom: Judul, Penulis, Tahun, URL, Skor Relevansi, Ringkasan
- Data terstruktur untuk analisis lanjutan

### metadata.json

- Informasi penelitian (tanggal, jumlah sumber, dll)
- Statistik per tipe sumber
- Distribusi skor relevansi

## 🔍 Search Sources

### Government Sources

- **BPS.go.id** - Statistik pendidikan dan ketenagakerjaan
- **Kemdikbud.go.id** - Kebijakan dan program pendidikan
- **Kemnaker.go.id** - Data ketenagakerjaan dan pelatihan

### International Sources

- **World Bank** - Development reports Indonesia
- **UNESCO** - Education statistics dan policies
- **ILO** - Labour market data

### Academic Sources

- **Google Scholar** - Peer-reviewed articles
- **ResearchGate** - Academic publications
- **Academia.edu** - Research papers

## 📈 Data Extraction

Tool ini mengekstrak data penting seperti:

- **Partisipasi SMK**: Jumlah/persentase siswa SMK
- **Tingkat Pengangguran**: Employment rate lulusan vokasi
- **Akses Internet**: Penetrasi internet di daerah
- **Literasi Digital**: Kemampuan digital masyarakat
- **Platform EdTech**: Adopsi teknologi pendidikan
- **Sertifikasi Digital**: Program sertifikasi kompetensi

## ⚙️ Configuration

Edit `config.json` untuk:

- Mengubah keywords pencarian
- Menyesuaikan pattern ekstraksi data
- Mengatur performance settings
- Mengubah threshold kualitas

## 🎯 Use Cases

### Untuk GEMASTIK

1. **Background Research** - Kumpulkan data pendukung proposal
2. **Literature Review** - Otomatis compile referensi
3. **Market Analysis** - Analisis kompetitor dan gap
4. **Data Validation** - Verifikasi asumsi dengan data terbaru

### Untuk Academic Research

1. **Systematic Review** - Kumpulkan sumber secara sistematis
2. **Meta-Analysis** - Ekstrak data untuk analisis meta
3. **Trend Analysis** - Identifikasi tren dari tahun ke tahun
4. **Policy Analysis** - Analisis kebijakan pemerintah

### Untuk Industry Analysis

1. **Market Research** - Riset pasar pendidikan vokasi
2. **Competitive Intelligence** - Analisis pemain industri
3. **Technology Trends** - Identifikasi teknologi emerging
4. **Investment Research** - Data untuk keputusan investasi

## 🔧 Technical Features

### Memory Optimization

- Batasan konten per sumber (5KB)
- Sequential processing vs parallel
- Garbage collection otomatis
- Cache management

### Rate Limiting

- 2 detik delay antar request
- Timeout 15 detik per request
- Max 3 retry per sumber
- User-agent rotation

### Error Handling

- Robust error catching
- Graceful degradation
- Logging komprehensif
- Fallback mechanisms

### Quality Control

- Relevance scoring (0-5)
- Content length validation
- Summary quality check
- Duplicate detection

## 📊 Performance Benchmarks

### Low-Spec Laptop (4GB RAM)

- **Max Sources**: 15 recommended, 25 maximum
- **Processing Time**: 5-10 menit untuk 15 sumber
- **Memory Usage**: ~200-400MB peak
- **Output Size**: ~2-5MB total

### Mid-Spec Laptop (8GB RAM)

- **Max Sources**: 25 recommended, 50 maximum
- **Processing Time**: 8-15 menit untuk 25 sumber
- **Memory Usage**: ~400-800MB peak
- **Output Size**: ~5-10MB total

## 🚨 Troubleshooting

### Common Issues

1. **"Request failed" errors**

   - Cek koneksi internet
   - Beberapa situs block scraping
   - Kurangi max_sources

2. **Memory errors**

   - Tutup aplikasi lain
   - Kurangi max_sources ke 10
   - Restart virtual environment

3. **Empty results**

   - Coba ubah keywords
   - Periksa tahun range
   - Verify sumber masih accessible

4. **Slow performance**
   - Increase request delay di config
   - Reduce max_sources
   - Check internet speed

### Debug Mode

```bash
python main.py --topic "test" --max_sources 3 --summarize
```

### Logs Location

- Terminal output shows progress
- Error details in stdout/stderr
- metadata.json contains stats

## 🔄 Future Enhancements

### Planned Features

1. **API Integration** - Official APIs untuk sumber data
2. **ML Relevance Scoring** - Machine learning untuk scoring
3. **Advanced NLP** - Better summarization dengan transformer
4. **Real-time Updates** - Monitoring sumber untuk update
5. **Web Interface** - GUI untuk non-technical users

### Extensibility

- Plugin system untuk sumber baru
- Custom extraction rules
- Multiple output formats
- Integration dengan tools lain

---

**LUMIRA Research Assistant v1.0** - Built for Indonesian Vocational Education Research 🇮🇩
