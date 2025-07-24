# LUMIRA Research Assistant 🔍

Research assistant AI untuk mengumpulkan, meringkas, dan mengorganisir data serta artikel terkini tentang pendidikan vokasi digital dan kesenjangan akses di Indonesia.

## 🎯 Fitur Utama

- **Pencarian Multi-Platform**: Google Scholar, sumber pemerintah (BPS, Kemendikbud, Kemenaker), institusi internasional (World Bank, UNESCO)
- **Ringkasan Otomatis**: Ringkasan 100-200 kata dalam Bahasa Indonesia
- **Ekstraksi Data**: Mengambil data penting seperti angka partisipasi, persentase, tren
- **Scoring Relevansi**: Penilaian 0-5 untuk setiap sumber
- **Export Multi-Format**: Markdown, Excel, CSV
- **Optimized untuk Low-Spec**: Dirancang untuk laptop <= 4GB RAM

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan dengan Konfigurasi Default

```bash
python riset_agent.py
```

### 3. Jalankan dengan Parameter Custom

```bash
python riset_agent.py --topic "akses pendidikan vokasi di Indonesia" --tahun 2021-2025 --output_folder "Riset Vokasi Indonesia – LUMIRA" --max_sources 15 --lang "id" --summarize --extract_data
```

## 📋 Parameter Command Line

| Parameter         | Default                                | Deskripsi                              |
| ----------------- | -------------------------------------- | -------------------------------------- |
| `--topic`         | "akses pendidikan vokasi di Indonesia" | Topik penelitian                       |
| `--tahun`         | "2021-2025"                            | Rentang tahun pencarian                |
| `--output_folder` | "Riset Vokasi Indonesia – LUMIRA"      | Folder output                          |
| `--max_sources`   | 15                                     | Maksimal sumber yang dikumpulkan       |
| `--lang`          | "id"                                   | Bahasa ringkasan (id/en)               |
| `--summarize`     | -                                      | Generate ringkasan untuk setiap sumber |
| `--download`      | -                                      | Download file PDF (jika tersedia)      |
| `--extract_data`  | -                                      | Extract data penting dari sumber       |

## 📁 Output Structure

```
Riset Vokasi Indonesia – LUMIRA/
├── Laporan_Riset_Lengkap.md      # Master report dalam Markdown
├── Database_Sumber_Riset.xlsx    # Database Excel dengan semua sumber
├── Database_Sumber_Riset.csv     # Database CSV alternatif
└── metadata.json                 # Metadata penelitian
```

## 📊 Format Laporan Master

### 1. Executive Summary

- Ringkasan penelitian dan temuan utama

### 2. Daftar Sumber

- Tabel lengkap semua sumber dengan scoring relevansi

### 3. Ringkasan Per Sumber

- Detail setiap sumber dengan ringkasan Bahasa Indonesia
- Data penting yang diekstrak
- Link ke sumber asli

### 4. Data Penting

- Kompilasi metrics utama dari semua sumber
- Angka partisipasi, persentase pengangguran, dll.

### 5. Rekomendasi

- Saran berdasarkan analisis untuk pengembangan platform vokasi

## 🔍 Sumber Data

### Pemerintah Indonesia

- **BPS** (Badan Pusat Statistik)
- **Kemendikbud** (Kementerian Pendidikan dan Kebudayaan)
- **Kemenaker** (Kementerian Ketenagakerjaan)

### Institusi Internasional

- **World Bank** (Bank Dunia)
- **UNESCO** (United Nations Educational, Scientific and Cultural Organization)
- **ILO** (International Labour Organization)

### Akademik & Riset

- **Google Scholar** - Artikel jurnal dan paper akademik
- **ResearchGate** - Platform penelitian akademik
- **Academia.edu** - Repository akademik

### Industri

- **EdTech Reports** - Laporan industri teknologi pendidikan
- **Vocational Platform Whitepapers** - Dokumen dari platform vokasi

## 🛠️ Optimasi untuk Low-Spec

- **Memory Management**: Batasan konten per sumber (5000 karakter)
- **Rate Limiting**: Delay antar request untuk menghindari overload
- **Sequential Processing**: Hindari parallel processing yang berat
- **Lightweight Dependencies**: Pilih library yang ringan
- **Batch Processing**: Proses sumber dalam batch kecil

## 📈 Contoh Data yang Diekstrak

- **Angka Partisipasi SMK**: Persentase siswa di SMK
- **Tingkat Pengangguran Lulusan**: Data employment rate
- **Akses Internet**: Persentase akses digital di daerah
- **Literasi Digital**: Tingkat kemampuan digital masyarakat
- **Platform EdTech**: Adopsi teknologi pendidikan

## 🎯 Use Case untuk GEMASTIK

Tool ini sangat cocok untuk:

1. **Riset Background** proposal GEMASTIK bidang pendidikan
2. **Data Supporting** untuk justifikasi masalah
3. **Literature Review** otomatis dan terstruktur
4. **Competitive Analysis** platform vokasi existing
5. **Market Research** industri pendidikan digital Indonesia

## 🚀 Advanced Usage

### Pencarian Khusus Topik

```bash
python main.py --topic "SMK digital transformation" --max_sources 20
```

### Export Only (tanpa summarize)

```bash
python main.py --topic "vocational education technology" --extract_data
```

### Riset Bahasa Inggris

```bash
python main.py --lang "en" --topic "digital divide education Indonesia"
```

## 🔧 Troubleshooting

### Error "Request Failed"

- Periksa koneksi internet
- Beberapa situs mungkin memblokir scraping
- Coba kurangi `--max_sources`

### Memory Error pada Low-Spec

- Kurangi `--max_sources` ke 10 atau kurang
- Tutup aplikasi lain yang berat
- Restart Python environment

### Hasil Sedikit

- Coba variasi keyword di `--topic`
- Periksa apakah tahun yang diminta memiliki banyak publikasi
- Beberapa sumber mungkin tidak accessible

## 📞 Support

Untuk pertanyaan atau masalah:

1. Periksa log error di terminal
2. Cek file `metadata.json` untuk statistik pencarian
3. Verify konten `Laporan_Riset_Lengkap.md` untuk kualitas hasil

## 🔄 Update & Development

Tool ini dapat diperluas dengan:

- Integrasi API resmi (jika tersedia)
- Machine learning untuk better relevance scoring
- Advanced NLP untuk summarization
- Database integration untuk historical data
- Real-time monitoring untuk update otomatis

---

**LUMIRA Research Assistant** - Empowering Indonesian Vocational Education Research 🇮🇩
