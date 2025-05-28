# finalproject_multimedia
# Filter Pemilihan Pemain Bola Terbaik Berbasis Facial Tracking

Proyek ini bertujuan untuk mengembangkan filter interaktif yang memungkinkan pengguna memilih pemain bola terbaik mereka menggunakan facial tracking secara real-time. Dengan memanfaatkan teknologi Python, OpenCV2, dan MediaPipe, filter ini memberikan pengalaman unik dan modern dalam menentukan starting lineup berdasarkan preferensi pengguna.

## Fitur Utama
1. Facial Tracking Real-Time
- Filter mengenali wajah pengguna secara langsung melalui kamera.
- Gerakan kepala digunakan untuk memilih antara dua pemain yang ditampilkan di layar.
2. Pemilihan Pemain Bola Favorit
- Pengguna disajikan komparasi visual dua pemain dalam setiap langkah pemilihan.
- Pemain bola yang dipilih merupakan pemain terbaik disetiap posisinya
3. Hasil Akhir yang Menarik
- Setelah seluruh pemilihan selesai, sistem akan menampilkan starting lineup berdasarkan pilihan pengguna.
- Pengguna juga akan ditampilkan nilai dari starting lineup tersebut

## Teknologi yang Digunakan
- Python untuk pengembangan logika dan integrasi keseluruhan.
- OpenCV2 untuk pengolahan video dan deteksi wajah secara real-time.
- MediaPipe untuk pelacakan gerakan kepala dan analisis gestur.

## Manfaat Proyek
- Hiburan: Pengguna dapat menciptakan tim impian mereka dengan cara yang interaktif dan menyenangkan.
- Edukasi: Memberikan wawasan tentang pemain bola dan peran mereka dalam sebuah tim.
- Inovasi Teknologi: Menggabungkan facial tracking dengan gamifikasi untuk meningkatkan pengalaman pengguna.
Proyek ini tidak hanya dirancang untuk menghibur, tetapi juga memperkenalkan pengguna pada pengalaman berbasis teknologi modern yang menggabungkan olahraga, data, dan kecerdasan buatan.
# Anggota Kelompok :
Abdi Maskur Mutaqin - 121140034 - AbdiMM11

# Logbook Mingguan

### Minggu 1
- Diskusi mengenai project yang akan dibuat
- Pembagian tugas tiap anggota kelompok

### Minggu 2
- Mulai mengerjakan project filter pemain bola
- Implementasi fitur face tracking dengan python

### Minggu 3
- Memperbaiki error pada codingan
- Menambahkan fitur value starting lineup diakhir

### Minggu 4
- Mengerjakan laporan
- Mengecek ulang codingan
- Memasukkan codingan ke github
- Penyusunan requirements.txt dan README.md.

# Instruksi instalansi dan penggunaan program
## Langkah Instalasi
1. Instal Python
- Pastikan Python 3.x sudah terinstal di komputer Anda. Jika belum, unduh dari Python Official Website.

2. Instal Library yang Dibutuhkan
- Instal library yang digunakan dalam proyek ini:
- Copy code pada terminal 
'''pip install opencv-python opencv-python-headless mediapipe numpy'''

4. Siapkan Gambar Pemain
- Letakkan file gambar pemain di direktori yang sama dengan file program Python.
- Pastikan nama file sesuai dengan yang tercantum di kode, seperti:
  - gk1.jpg
  - cb1.jpg
  - cf1.jpg
  Dan sebagainya.
  Program akan mencetak pesan kesalahan jika gambar tidak ditemukan.

5. Jalankan Program
- Simpan kode dalam file starting_eleven.py, lalu jalankan program dengan perintah:
Copy code di terminal
'''python starting_eleven.py'''

## Penggunaan Program
1. Pastikan kamera aktif dan dapat digunakan.
2. Program akan menampilkan dua gambar pemain bola.
3. Gerakkan kepala ke kiri atau ke kanan untuk memilih salah satu pemain.
4. Setelah semua posisi terisi, program akan menampilkan formasi tim berdasarkan pilihan Anda dan value dari tim tersebut.
