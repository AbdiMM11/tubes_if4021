# 🏆 Filter Dream Team

Filter ini dirancang untuk membuat filter interaktif yang memungkinkan pengguna memilih pemain sepak bola favorit mereka dengan melacak wajah mereka secara real-time. Dengan mengintegrasikan teknologi Python, OpenCV2, dan MediaPipe, filter ini memberikan pengalaman modern dan menarik dalam menyusun starting lineup sesuai preferensi pengguna.

## ✨ Highlight Fitur

### 🎯 **Kontrol Hands-Free dengan Nose Tracking**
- Sistem kontrol inovatif menggunakan gerakan hidung untuk navigasi
- Miringkan hidung ke **kiri** atau **kanan** untuk memilih pemain
- Tahan posisi selama **1 detik** untuk konfirmasi pilihan
- Interface yang responsif dan mudah digunakan

### ⚽ **Sistem Seleksi Pemain Profesional**
- Database lengkap dengan **44 pemain** dari berbagai posisi
- Setiap pemain memiliki **rating individual** berdasarkan performa
- Formasi taktis **4-3-3** yang populer dalam sepak bola modern
- Algoritma seleksi yang memastikan variasi pilihan setiap sesi

### 📊 **Analisis Tim Komprehensif**
- Kalkulasi **total rating tim** secara otomatis
- Sistem penilaian bertingkat dari **"WEAK TEAM"** hingga **"LEGENDARY TEAM"**
- Visualisasi formasi profesional layaknya dalam permainan sungguhan
- Interface yang menarik dengan tata letak pemain yang akurat

## 🛠️ Teknologi Canggih

| Teknologi | Fungsi |
|-----------|--------|
| **Python 3.x** | Engine utama dan logika aplikasi |
| **OpenCV 4.x** | Computer Vision dan pemrosesan video real-time |
| **MediaPipe** | AI Framework untuk deteksi landmark wajah |
| **NumPy** | Komputasi numerik dan manipulasi array |

## 👥 Tim Pengembang

| Nama Lengkap | NIM | GitHub Profile |
|--------------|-----|----------------|
| **Abdi Maskur Mutaqin** | 121140034 | [@AbdiMM11](https://github.com/AbdiMM11) |
| **Idza Ramaulkim** | 121140152 | [@Idza-Ramaulkim-121140152](https://github.com/Idza-Ramaulkim-121140152) |
| **Silvester Adrian Sitanggang** | 121140153 | [@SilvesterASTG](https://github.com/SilvesterASTG) |

## 📅 Logbook Pengembangan

### 🗓️ **Minggu 1 (Inisiasi Project)**
- **Brainstorming** konsep aplikasi team selection interaktif
- **Analisis kebutuhan** teknologi dan library yang diperlukan
- **Pembagian roles** dan tanggung jawab setiap anggota tim
- **Setup environment** pengembangan dan repository GitHub

### 🗓️ **Minggu 2 (Core Development)**
- **Implementasi face tracking** menggunakan MediaPipe
- **Pengembangan sistem kontrol** berbasis gerakan hidung
- **Integrasi OpenCV** untuk real-time video processing
- **Testing** algoritma deteksi dan akurasi tracking

### 🗓️ **Minggu 3 (Feature Enhancement)**
- **Bug fixing** dan optimasi performa aplikasi
- **Implementasi sistem scoring** dan penilaian tim
- **Pengembangan UI/UX** yang lebih intuitif dan menarik
- **Penambahan feedback visual** untuk user experience

### 🗓️ **Minggu 4 (Finalisasi & Documentation)**
- **Code review** menyeluruh dan penambahan dokumentasi
- **Penyusunan laporan** dan technical documentation
- **Upload final version** ke GitHub repository
- **Pembuatan README.md** dan requirements.txt yang komprehensif

## 🚀 Panduan Instalasi

### 📋 **Prasyarat Sistem**
```bash
# Pastikan Python 3.7+ terinstal
python --version

# Pastikan pip package manager tersedia
pip --version
```

### 📦 **Instalasi Dependencies**
```bash
# Clone repository
git clone [repository-url]
cd team-selection-game

# Install required packages
pip install opencv-python opencv-python-headless mediapipe numpy

# Atau menggunakan requirements.txt
pip install -r requirements.txt
```

### 📁 **Struktur Direktori**
```
team-selection-game/
├── main.py                 # File utama aplikasi
├── asset/                  # Folder gambar pemain
│   ├── player_gk1.jpg
│   ├── player_lb1.jpg
│   └── ... (44 gambar pemain)
├── requirements.txt        # Dependencies list
└── README.md              # Dokumentasi ini
```

### 🖼️ **Setup Asset Gambar**
- Letakkan **44 gambar pemain** dalam folder `asset/`
- Format nama file: `player_[kode_pemain].jpg`
- Contoh: `player_gk1.jpg`, `player_cf1.jpg`, dll.
- Jika gambar tidak tersedia, sistem akan generate **placeholder otomatis**

## 🎮 Cara Penggunaan

### 🎯 **Langkah-langkah Bermain**

1. **Persiapan**
   ```bash
   python main.py
   ```

2. **Kalibrasi Kamera**
   - Pastikan **wajah terdeteksi** dengan baik
   - Posisikan diri dalam **pencahayaan yang cukup**
   - Hindari **background yang kompleks**

3. **Kontrol Game**
   - 👈 **Miringkan hidung ke KIRI** → Pilih pemain kiri
   - 👉 **Miringkan hidung ke KANAN** → Pilih pemain kanan
   - ⏱️ **Tahan posisi 1 detik** → Konfirmasi pilihan
   - ❌ **Tekan 'Q'** → Keluar dari aplikasi

4. **Proses Seleksi**
   - Pilih pemain untuk **11 posisi** (GK, LB, LCB, RCB, RB, CMF, DMF, CMF, LWF, CF, RWF)
   - Setiap posisi menampilkan **2 opsi pemain random**
   - **Progress bar** menunjukkan kemajuan hold gesture
   - **Cooldown 2 detik** antar seleksi untuk stabilitas

5. **Hasil Akhir**
   - Formasi **4-3-3** dengan pemain terpilih
   - **Total rating tim** dan kategori performa
   - Tampilan hasil selama **10 detik**

### 🎛️ **Tips Penggunaan Optimal**

| Aspek | Rekomendasi |
|-------|-------------|
| **Pencahayaan** | Cahaya terang, hindari backlight |
| **Posisi Kamera** | Sejajar dengan wajah, jarak 50-100cm |
| **Gerakan** | Gerakan hidung yang **jelas** dan **konsisten** |
| **Stabilitas** | Kepala relatif stabil, hanya hidung yang bergerak |

### 🏆 **Sistem Penilaian Tim**

| Total Rating | Kategori | Deskripsi |
|--------------|----------|-----------|
| **900+** | 🏆 LEGENDARY TEAM | Tim dengan pemain bintang di setiap lini |
| **800-899** | ⭐ EXCELLENT TEAM | Tim yang sangat kompetitif dan seimbang |
| **700-799** | ✅ GOOD TEAM | Tim solid dengan kualitas di atas rata-rata |
| **600-699** | 📊 DECENT TEAM | Tim yang cukup baik untuk kompetisi menengah |
| **<600** | 📉 WEAK TEAM | Tim yang membutuhkan peningkatan signifikan |

## 🔧 Troubleshooting

### ❌ **Masalah Umum dan Solusi**

| Masalah | Penyebab | Solusi |
|---------|----------|--------|
| Kamera tidak terdeteksi | Driver atau permission | Restart aplikasi, cek camera permission |
| Face tracking tidak akurat | Pencahayaan buruk | Perbaiki lighting, hindari shadow |
| Lag atau freeze | Hardware limitation | Tutup aplikasi lain, restart program |
| Gambar pemain tidak muncul | File asset tidak lengkap | Cek folder asset/, nama file harus sesuai |

<div align="center">

**🎮 Selamat bermain dan semoga berhasil membangun tim impian Anda! ⚽**
</div>
