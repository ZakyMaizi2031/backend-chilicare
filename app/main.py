import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# Import komponen internal sesuai struktur folder
from app.database import engine, Base, SessionLocal
from app.models import User, Penyakit, Rekomendasi, Artikel
from app.api import auth, encyclopedia, detection, admin, artikel, history
from app.core.config import settings
from app.services import ml_service

# 1. LIFESPAN CONTEXT MANAGER (Pengganti startup/shutdown event yang deprecated)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n[DEBUG-STARTUP] Memulai proses startup...")
    # Membuat tabel jika belum ada
    print("[DEBUG-STARTUP] Menyambung ke Database MySQL...")
    Base.metadata.create_all(bind=engine)
    print("[DEBUG-STARTUP] Database siap!")
    
    # Load ML Model first
    print("[DEBUG-STARTUP] Memuat model Machine Learning...")
    ml_service.load_model()
    
    db = SessionLocal()
    try:
        print("\n>>> [SYSTEM] Menjalankan Sinkronisasi Data ChiliCare...")

        # --- A. Pembuatan Akun Admin Otomatis ---
        admin_email = settings.ADMIN_EMAIL
        admin_exists = db.query(User).filter(User.email == admin_email).first()
        
        if not admin_exists:
            from app.core.security import get_password_hash
            new_admin = User(
                nama_lengkap="Administrator ChiliCare",
                email=admin_email,
                password=get_password_hash(settings.ADMIN_PASSWORD), # Password admin di-hash
                role="admin"
            )
            db.add(new_admin)
            db.commit()
            print(f"[SEED] Akun Admin Siap: {admin_email}")

        # --- B. Pengisian Data Ensiklopedia (5 Kelas Penyakit) ---
        if db.query(Penyakit).count() == 0:
            master_data = [
                {
                    "nama": "Antraknosa",
                    "gejala": "Bercak coklat kehitaman pada buah cabai, melingkar seperti pusaran api.",
                    "penyebab": "Jamur Colletotrichum capsici",
                    "obat": "Fungisida Mankozeb atau Propinib.",
                    "langkah": "Musnahkan buah terinfeksi, atur jarak tanam agar tidak terlalu lembab."
                },
                {
                    "nama": "BusukBuah",
                    "gejala": "Buah melunak, berair, warna memucat, dan berbau busuk. Sering menular dengan cepat ke buah lain.",
                    "penyebab": "Bakteri Erwinia carotovora atau Lalat Buah",
                    "obat": "Bakterisida Streptomisin atau perangkap lalat buah (Petrogenol).",
                    "langkah": "Segera petik dan buang buah yang membusuk jauh dari lahan, perbaiki drainase, dan kurangi kelembapan."
                },
                {
                    "nama": "BercakHitamAlternaria",
                    "gejala": "Terdapat bercak-bercak hitam tidak beraturan pada buah atau daun, lama-kelamaan membesar dan membuat buah mengkerut atau cacat.",
                    "penyebab": "Jamur Alternaria solani / Alternaria spp.",
                    "obat": "Fungisida berbahan aktif Difenokonazol atau Klorotalonil.",
                    "langkah": "Semprotkan fungisida secara merata, jaga kebersihan kebun dari gulma, dan pastikan sirkulasi udara antar tanaman baik."
                },
                {
                    "nama": "Sehat",
                    "gejala": "Buah berwarna merah/hijau merata, tekstur kencang, kulit mulus tanpa bercak.",
                    "penyebab": "Perawatan Optimal",
                    "obat": "Pupuk NPK seimbang dan rutin penyiraman.",
                    "langkah": "Pertahankan kebersihan lahan, berikan nutrisi berimbang, dan pantau tanaman secara berkala."
                }
            ]

            for item in master_data:
                # 1. Simpan ke tabel Penyakit
                p = Penyakit(
                    nama_penyakit=item['nama'],
                    gejala_visual=item['gejala'],
                    penyebab=item['penyebab'],
                    foto_referensi=f"static/placeholder_{item['nama'].lower()}.jpg"
                )
                db.add(p)
                db.flush() # Mendapatkan ID penyakit untuk relasi

                # 2. Simpan ke tabel Rekomendasi (Terhubung via ID)
                r = Rekomendasi(
                    id_penyakit=p.id_penyakit,
                    langkah_penanganan=item['langkah'],
                    nama_obat=item['obat']
                )
                db.add(r)
            
            db.commit()
            print("[SEED] Master Data Ensiklopedia Berhasil Disuntikkan!")

    except Exception as e:
        print(f"[ERROR] Seeding gagal: {e}")
        db.rollback()
    finally:
        db.close()
        print(">>> [SYSTEM] Sinkronisasi Selesai.\n")
        
    yield

# 2. INISIALISASI APP DENGAN LIFESPAN
app = FastAPI(
    title="ChiliCare Backend API",
    description="Sistem Deteksi Penyakit Cabai Merah & Manajemen Ensiklopedia",
    version="1.0.0",
    lifespan=lifespan
)

# 3. KONFIGURASI CORS (PENTING: Agar Flutter & Web Dashboard bisa akses API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. KONFIGURASI FOLDER STATIC (Untuk simpan & tampilkan foto hasil scan)
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Folder static bisa diakses via URL: http://localhost:8000/static/...
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# 5. REGISTRASI ROUTER (Menghubungkan endpoint API)
app.include_router(auth.router)           # Login & Register
app.include_router(encyclopedia.router)   # Katalog Penyakit untuk Petani
app.include_router(detection.router)      # Proses Deteksi CNN
app.include_router(admin.router)          # CRUD Dashboard Admin
app.include_router(artikel.router)        # Artikel Encyclopedia Mandiri
app.include_router(history.router)        # Riwayat Deteksi

# 7. ENDPOINT ROOT (Untuk Cek Status Server & Health Check)
@app.api_route("/", methods=["GET", "HEAD"], tags=["Root"])
def check_status():
    return {
        "project": "ChiliCare API",
        "status": "Online",
        "database": "Connected",
        "docs": "/docs"
    }