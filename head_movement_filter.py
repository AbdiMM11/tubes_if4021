import cv2
import numpy as np
import mediapipe as mp
import time
import random
import os
import logging

# Menekan peringatan MediaPipe untuk mengurangi output tidak penting
logging.getLogger('mediapipe').setLevel(logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Dictionary yang berisi rating/poin untuk setiap pemain
# Format: "kode_pemain": rating_numerik
player_points = {
    "gk1": 78, "gk2": 85, "gk3": 80, "gk4": 90,       # Goalkeeper (Penjaga Gawang)
    "lb1": 89, "lb2": 83, "lb3": 78, "lb4": 87,       # Left Back (Bek Kiri)
    "lcb1": 91, "lcb2": 87, "lcb3": 85, "lcb4": 84,   # Left Center Back (Bek Tengah Kiri)
    "rcb1": 79, "rcb2": 88, "rcb3": 90, "rcb4": 76,   # Right Center Back (Bek Tengah Kanan)
    "rb1": 86, "rb2": 84, "rb3": 85, "rb4": 81,       # Right Back (Bek Kanan)
    "cmf1": 85, "cmf2": 87, "cmf3": 86, "cmf4": 89,   # Central Midfielder (Gelandang Tengah)
    "dmf1": 88, "dmf2": 87, "dmf3": 83, "dmf4": 85,   # Defensive Midfielder (Gelandang Bertahan)
    "cmf5": 87, "cmf6": 86, "cmf7": 84, "cmf8": 82,   # Central Midfielder tambahan
    "lwf1": 93, "lwf2": 87, "lwf3": 84, "lwf4": 90,   # Left Wing Forward (Sayap Kiri)
    "cf1": 95, "cf2": 90, "cf3": 88, "cf4": 91,       # Center Forward (Penyerang Tengah)
    "rwf1": 89, "rwf2": 87, "rwf3": 91, "rwf4": 83    # Right Wing Forward (Sayap Kanan)
}

# List posisi tim dengan formasi 4-3-3
# Setiap posisi memiliki 4 pilihan pemain yang tersedia
positions = [
    {"name": "GK", "options": ["gk1", "gk2", "gk3", "gk4"]},      # Penjaga Gawang
    {"name": "LB", "options": ["lb1", "lb2", "lb3", "lb4"]},      # Bek Kiri
    {"name": "LCB", "options": ["lcb1", "lcb2", "lcb3", "lcb4"]}, # Bek Tengah Kiri
    {"name": "RCB", "options": ["rcb1", "rcb2", "rcb3", "rcb4"]}, # Bek Tengah Kanan
    {"name": "RB", "options": ["rb1", "rb2", "rb3", "rb4"]},      # Bek Kanan
    {"name": "CMF", "options": ["cmf1", "cmf2", "cmf3", "cmf4"]}, # Gelandang Tengah 1
    {"name": "DMF", "options": ["dmf1", "dmf2", "dmf3", "dmf4"]}, # Gelandang Bertahan
    {"name": "CMF", "options": ["cmf5", "cmf6", "cmf7", "cmf8"]}, # Gelandang Tengah 2
    {"name": "LWF", "options": ["lwf1", "lwf2", "lwf3", "lwf4"]}, # Sayap Kiri
    {"name": "CF", "options": ["cf1", "cf2", "cf3", "cf4"]},      # Penyerang Tengah
    {"name": "RWF", "options": ["rwf1", "rwf2", "rwf3", "rwf4"]}  # Sayap Kanan
]

def load_player_images():
    """
    Memuat semua gambar pemain dari folder asset.
    
    Tujuan:
        Mengambil gambar setiap pemain untuk ditampilkan dalam interface game
    
    Parameters:
        Tidak ada parameter input
    
    Returns:
        dict: Dictionary berisi gambar setiap pemain dengan kode pemain sebagai key
              Format: {"kode_pemain": image_array}
    
    Catatan:
        - Jika gambar tidak ditemukan, akan membuat gambar dummy berwarna random
        - Gambar dummy akan diberi label nama pemain
    """
    asset_path = "asset"  # Path folder yang berisi gambar pemain
    images = {}           # Dictionary untuk menyimpan gambar
    
    # Loop melalui setiap posisi dan setiap pemain
    for position in positions:
        for player in position["options"]:
            # Konstruksi path file gambar
            img_path = os.path.join(asset_path, f"player_{player}.jpg")
            img = cv2.imread(img_path)  # Membaca gambar
            
            # Jika gambar tidak ditemukan, buat gambar dummy
            if img is None:
                # Membuat rectangle berwarna random sebagai pengganti
                img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
                # Menambahkan text nama pemain pada gambar dummy
                cv2.putText(img, player.upper(), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            images[player] = img  # Menyimpan gambar ke dictionary
    
    return images

def get_nose_direction(landmarks, frame_width):
    """
    Mendeteksi arah kemiringan hidung untuk sistem kontrol seleksi.
    
    Tujuan:
        Menganalisis posisi hidung relatif terhadap wajah untuk menentukan arah tilt
    
    Parameters:
        landmarks: Landmark wajah dari MediaPipe yang berisi koordinat titik-titik wajah
        frame_width (int): Lebar frame video untuk normalisasi koordinat
    
    Returns:
        str: Arah kemiringan hidung ("left", "right", atau "center")
    
    Logika:
        - Mengambil koordinat ujung hidung dan kedua pipi
        - Menghitung pusat wajah berdasarkan posisi pipi
        - Membandingkan posisi hidung dengan pusat wajah
        - Menentukan arah berdasarkan threshold yang telah ditentukan
    """
    # Mengambil titik landmark penting dari wajah
    nose_tip = landmarks.landmark[1]      # Ujung hidung (landmark index 1)
    left_cheek = landmarks.landmark[234]  # Pipi kiri (landmark index 234)
    right_cheek = landmarks.landmark[454] # Pipi kanan (landmark index 454)
    
    # Menghitung koordinat x pusat wajah berdasarkan rata-rata posisi pipi
    face_center_x = (left_cheek.x + right_cheek.x) / 2
    
    # Menghitung offset/selisih posisi hidung dari pusat wajah
    nose_offset = nose_tip.x - face_center_x
    
    # Threshold untuk sensitivitas deteksi kemiringan hidung
    # Nilai kecil = lebih sensitif, nilai besar = kurang sensitif
    tilt_threshold = 0.02
    
    # Logika penentuan arah berdasarkan offset
    if nose_offset > tilt_threshold:
        return "right"  # Hidung miring ke kanan
    elif nose_offset < -tilt_threshold:
        return "left"   # Hidung miring ke kiri
    else:
        return "center" # Hidung di posisi tengah/normal

def create_result_display(selected_players, player_images):
    """
    Membuat tampilan formasi tim final dengan layout 4-3-3.
    
    Tujuan:
        Menampilkan hasil seleksi tim dalam bentuk formasi sepak bola yang visual
    
    Parameters:
        selected_players (list): List berisi kode pemain yang telah dipilih
        player_images (dict): Dictionary berisi gambar setiap pemain
    
    Returns:
        numpy.ndarray: Image array yang berisi tampilan formasi tim lengkap
    
    Fitur:
        - Menata pemain sesuai formasi 4-3-3
        - Menampilkan rating setiap pemain
        - Menghitung total skor tim
        - Memberikan penilaian kualitas tim berdasarkan total skor
    """
    # Membuat canvas kosong berwarna hijau gelap (seperti lapangan)
    canvas = np.ones((720, 1280, 3), dtype=np.uint8) * 34
    
    # Posisi koordinat untuk formasi 4-3-3 (x, y)
    # Disusun dari belakang ke depan: GK -> Defense -> Midfield -> Attack
    formation_positions = [
        (640, 620),  # GK (Penjaga Gawang)
        # Lini Pertahanan (4 pemain)
        (320, 480), (480, 480), (800, 480), (960, 480),  # LB, LCB, RCB, RB
        # Lini Tengah (3 pemain)
        (480, 340), (640, 320), (800, 340),  # CMF, DMF, CMF
        # Lini Serang (3 pemain)
        (400, 180), (640, 150), (880, 180)   # LWF, CF, RWF
    ]
    
    total_score = 0  # Variabel untuk menghitung total skor tim
    
    # Loop untuk menempatkan setiap pemain pada posisi formasi
    for i, player in enumerate(selected_players[:11]):  # Maksimal 11 pemain
        if i < len(formation_positions):
            x, y = formation_positions[i]  # Koordinat posisi pemain
            
            # Resize gambar pemain menjadi 80x80 pixel dan tempatkan di canvas
            img = cv2.resize(player_images[player], (80, 80))
            canvas[y:y+80, x-40:x+40] = img
            
            # Menambahkan rating pemain di bawah gambar
            score = player_points[player]
            total_score += score  # Akumulasi total skor
            cv2.putText(canvas, f"{score}", (x-15, y+100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Sistem penilaian kualitas tim berdasarkan total skor
    if total_score >= 900:
        rating = "LEGENDARY TEAM!"   # Tim legendaris (900+)
    elif total_score >= 800:
        rating = "EXCELLENT TEAM!"   # Tim excellent (800-899)
    elif total_score >= 700:
        rating = "GOOD TEAM"         # Tim bagus (700-799)
    elif total_score >= 600:
        rating = "DECENT TEAM"       # Tim lumayan (600-699)
    else:
        rating = "WEAK TEAM"         # Tim lemah (<600)
    
    # Menampilkan total skor dan rating tim di bagian atas canvas
    cv2.putText(canvas, f"Total: {total_score}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.putText(canvas, rating, (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
    
    return canvas

def main():
    """
    Fungsi utama yang menjalankan game seleksi tim.
    
    Tujuan:
        Mengatur alur utama permainan seleksi tim menggunakan kontrol gerakan hidung
    
    Parameters:
        Tidak ada parameter input
    
    Returns:
        Tidak ada return value (void function)
    
    Alur Program:
        1. Inisialisasi kamera dan MediaPipe
        2. Load gambar pemain
        3. Loop utama game untuk setiap posisi
        4. Deteksi gerakan hidung untuk kontrol
        5. Proses seleksi pemain
        6. Tampilkan hasil akhir formasi tim
    
    Kontrol Game:
        - Miringkan hidung ke kiri/kanan untuk memilih
        - Tahan posisi selama 1 detik untuk konfirmasi
        - Tekan 'q' untuk keluar prematur
    """
    # Inisialisasi kamera dengan error handling
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
        
    # Pengaturan properti kamera untuk performa optimal
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Lebar frame
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Tinggi frame
    cap.set(cv2.CAP_PROP_FPS, 30)            # Frame rate
    
    # Inisialisasi MediaPipe Face Mesh
    mp_face_mesh = mp.solutions.face_mesh
    
    # Load semua gambar pemain
    player_images = load_player_images()
    
    # === VARIABEL STATE GAME ===
    current_position = 0      # Posisi yang sedang dipilih (index dari positions array)
    selected_players = []     # List pemain yang sudah dipilih
    last_action_time = 0      # Waktu aksi terakhir (untuk cooldown)
    action_cooldown = 2.0     # Cooldown 2 detik antara seleksi
    
    # === VARIABEL TAMPILAN OPSI ===
    current_options = None           # Opsi pemain yang sedang ditampilkan
    option_display_time = 0          # Waktu mulai menampilkan opsi
    show_options_duration = 3.0      # Durasi menampilkan opsi (3 detik)
    
    # === VARIABEL KONTROL HIDUNG ===
    tilt_start_time = 0              # Waktu mulai tilt hidung
    current_tilt_direction = "center" # Arah tilt saat ini
    hold_duration = 1.0              # Durasi hold yang diperlukan (1 detik)
    is_holding = False               # Status apakah sedang hold
    
    # Konfigurasi MediaPipe Face Mesh
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,              # Maksimal 1 wajah yang dideteksi
        refine_landmarks=False,       # Nonaktifkan refine untuk mengurangi warning
        min_detection_confidence=0.7, # Confidence minimum untuk deteksi
        min_tracking_confidence=0.7,  # Confidence minimum untuk tracking
        static_image_mode=False       # Mode video (bukan gambar statis)
    ) as face_mesh:
        
        # === MAIN GAME LOOP ===
        # Loop berlanjut selama kamera terbuka dan belum selesai memilih semua posisi
        while cap.isOpened() and current_position < len(positions):
            ret, frame = cap.read()  # Baca frame dari kamera
            if not ret:
                print("Cannot read from camera")
                break
            
            # Mendapatkan dimensi frame dan membalik horizontal (mirror effect)
            frame_height, frame_width = frame.shape[:2]
            frame = cv2.flip(frame, 1)  # Mirror frame untuk UX yang lebih natural
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Konversi ke RGB
            
            # Proses frame dengan MediaPipe
            frame_rgb.flags.writeable = False  # Optimasi: set read-only
            results = face_mesh.process(frame_rgb)  # Deteksi wajah
            frame_rgb.flags.writeable = True   # Set kembali ke writable
            
            # Mendapatkan waktu saat ini dan informasi posisi
            current_time = time.time()
            position_info = positions[current_position]
            
            # === TAMPILAN UI UTAMA ===
            # Menampilkan posisi yang sedang dipilih
            cv2.putText(frame, f"Select {position_info['name']}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            
            # Menampilkan instruksi kontrol
            cv2.putText(frame, "Tilt nose LEFT/RIGHT and HOLD 1 sec", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # === GENERATE OPSI PEMAIN BARU ===
            # Jika belum ada opsi atau opsi sudah expired, buat opsi baru
            if current_options is None:
                # Ambil 2 pemain random dari 4 opsi yang tersedia untuk posisi ini
                current_options = random.sample(position_info["options"], 2)
                option_display_time = current_time
            
            # === TAMPILAN OPSI PEMAIN ===
            # Tampilkan opsi selama durasi yang ditentukan
            if current_time - option_display_time < show_options_duration:
                # Opsi kiri - gambar dan label
                left_img = cv2.resize(player_images[current_options[0]], (120, 120))
                frame[150:270, 100:220] = left_img  # Tempatkan gambar
                cv2.putText(frame, f"LEFT: {current_options[0].upper()}", (80, 290), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Opsi kanan - gambar dan label
                right_img = cv2.resize(player_images[current_options[1]], (120, 120))
                frame[150:270, 400:520] = right_img  # Tempatkan gambar
                cv2.putText(frame, f"RIGHT: {current_options[1].upper()}", (380, 290), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # === DETEKSI DAN PROSES KONTROL HIDUNG ===
            # Proses hanya jika ada wajah terdeteksi dan cooldown sudah habis
            if results.multi_face_landmarks and current_time - last_action_time > action_cooldown:
                try:
                    # Ambil landmark wajah pertama (index 0)
                    face_landmarks = results.multi_face_landmarks[0]
                    # Deteksi arah kemiringan hidung
                    nose_direction = get_nose_direction(face_landmarks, frame_width)
                    
                    # === LOGIKA HOLD MECHANISM ===
                    # Cek apakah arah berubah dari sebelumnya
                    if nose_direction != current_tilt_direction:
                        current_tilt_direction = nose_direction
                        # Jika mulai tilt ke kiri/kanan, mulai hitung waktu hold
                        if nose_direction in ["left", "right"]:
                            tilt_start_time = current_time
                            is_holding = True
                        else:
                            # Jika kembali ke center, stop holding
                            is_holding = False
                    
                    # Hitung progress hold (0.0 - 1.0)
                    hold_progress = 0
                    if is_holding and current_tilt_direction in ["left", "right"]:
                        hold_progress = min((current_time - tilt_start_time) / hold_duration, 1.0)
                    
                    # === TAMPILAN STATUS KONTROL ===
                    # Tampilkan arah hidung saat ini dengan warna
                    direction_color = (0, 255, 0) if current_tilt_direction in ["left", "right"] else (255, 0, 0)
                    cv2.putText(frame, f"Nose: {current_tilt_direction.upper()}", (50, 400), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, direction_color, 2)
                    
                    # Tampilkan progress bar untuk hold
                    if is_holding and current_tilt_direction in ["left", "right"]:
                        # Background progress bar (abu-abu)
                        cv2.rectangle(frame, (50, 430), (350, 460), (100, 100, 100), -1)
                        # Progress bar fill (hijau -> kuning saat hampir selesai)
                        progress_width = int(300 * hold_progress)
                        progress_color = (0, 255, 0) if hold_progress < 1.0 else (0, 255, 255)
                        cv2.rectangle(frame, (50, 430), (50 + progress_width, 460), progress_color, -1)
                        # Text persentase progress
                        cv2.putText(frame, f"Hold: {hold_progress:.1%}", (50, 480), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # === EKSEKUSI SELEKSI ===
                    # Jika hold sudah mencapai 100%, lakukan seleksi
                    if is_holding and hold_progress >= 1.0:
                        if current_tilt_direction == "left":
                            # Pilih opsi kiri
                            selected_players.append(current_options[0])
                            cv2.putText(frame, f"SELECTED: {current_options[0].upper()}!", (200, 520), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                            # Reset state untuk posisi berikutnya
                            current_position += 1
                            current_options = None
                            last_action_time = current_time
                            is_holding = False
                            
                        elif current_tilt_direction == "right":
                            # Pilih opsi kanan
                            selected_players.append(current_options[1])
                            cv2.putText(frame, f"SELECTED: {current_options[1].upper()}!", (200, 520), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                            # Reset state untuk posisi berikutnya
                            current_position += 1
                            current_options = None
                            last_action_time = current_time
                            is_holding = False
                
                except Exception as e:
                    # Handle error deteksi wajah tanpa menghentikan program
                    print(f"Face detection error: {e}")
                    pass
            
            # === TAMPILAN PROGRESS GAME ===
            # Menampilkan berapa posisi yang sudah dipilih
            cv2.putText(frame, f"Progress: {current_position}/{len(positions)}", (50, 550), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # Tampilkan frame hasil
            cv2.imshow("Team Selection", frame)
            
            # Cek input keyboard untuk keluar (tekan 'q')
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    # === TAMPILKAN HASIL AKHIR ===
    # Jika semua posisi sudah dipilih, tampilkan formasi tim
    if len(selected_players) == len(positions):
        result_display = create_result_display(selected_players, player_images)
        cv2.imshow("Your Team Formation", result_display)
        cv2.waitKey(10000)  # Tampilkan selama 10 detik
    
    # Cleanup: tutup kamera dan window
    cap.release()
    cv2.destroyAllWindows()

# === ENTRY POINT PROGRAM ===
# Blok ini memastikan main() hanya dijalankan jika file ini dieksekusi langsung
if __name__ == "__main__":
    main()
