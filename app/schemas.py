from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# ============================================================
# 1. SCHEMAS UNTUK USER & AUTH (Aplikasi Mobile & Web)
# ============================================================

class UserLogin(BaseModel):
    """Schema untuk request data saat user/admin login"""
    email: str
    password: str

class UserCreate(BaseModel):
    """Schema untuk pendaftaran user baru (Default role: petani)"""
    nama: str
    email: str
    password: str
    role: Optional[str] = "petani"

class UserUpdate(BaseModel):
    """Digunakan Admin untuk mengedit data pengguna di Web Dashboard"""
    nama_lengkap: Optional[str] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    """Data user yang dikirim balik ke frontend (tanpa password)"""
    id_user: int
    nama_lengkap: str
    email: str
    role: str
    foto_profil: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

# ============================================================
# 2. SCHEMAS UNTUK ENSIKLOPEDIA & REKOMENDASI (CRUD ADMIN)
# ============================================================

class RekomendasiBase(BaseModel):
    """Schema dasar untuk data rekomendasi penanganan"""
    langkah_penanganan: str
    nama_obat: str
    
    model_config = ConfigDict(from_attributes=True)

class PenyakitBase(BaseModel):
    """Schema dasar untuk menampilkan katalog penyakit"""
    id_penyakit: int
    nama_penyakit: str
    gejala_visual: str
    penyebab: str
    foto_referensi: Optional[str] = None
    rekomendasi: Optional[RekomendasiBase] = None
    
    model_config = ConfigDict(from_attributes=True)

class EncyclopediaCreate(BaseModel):
    """SCHEMA UTAMA: Digunakan Admin saat menambah penyakit baru melalui Web"""
    nama_penyakit: str
    gejala_visual: str
    penyebab: str
    langkah_penanganan: str # Input penanganan digabung di form yang sama
    nama_obat: str
    foto_referensi: Optional[str] = "static/placeholder.jpg"

class EncyclopediaUpdate(BaseModel):
    """Digunakan Admin saat mengedit data ensiklopedia"""
    nama_penyakit: Optional[str] = None
    gejala_visual: Optional[str] = None
    penyebab: Optional[str] = None
    langkah_penanganan: Optional[str] = None
    nama_obat: Optional[str] = None
    foto_referensi: Optional[str] = None


# ============================================================
# 3. SCHEMAS UNTUK DETEKSI & RIWAYAT (Aplikasi Mobile)
# ============================================================

class DetectionResponse(BaseModel):
    """Hasil yang dikembalikan ke Flutter setelah proses CNN selesai"""
    label: str
    confidence: float
    gejala: str
    penyebab: str
    langkah_penanganan: str
    nama_obat: str

class RiwayatResponse(BaseModel):
    """Detail riwayat deteksi untuk ditampilkan di list riwayat petani"""
    id_riwayat: int
    id_user: int
    hasil_prediksi: str
    tingkat_akurasi: float
    tanggal_deteksi: datetime
    file_foto_input: str
    # Relasi opsional
    nama_penyakit: Optional[str] = None 
    
    model_config = ConfigDict(from_attributes=True)

class RiwayatCreate(BaseModel):
    """Payload saat pengguna menyimpan riwayat deteksi secara manual"""
    id_user: int
    id_penyakit: int
    file_foto_input: str
    hasil_prediksi: str
    tingkat_akurasi: float


# ============================================================
# 4. SCHEMAS UNTUK ARTIKEL / ENCYCLOPEDIA MANDIRI
# ============================================================

class ArtikelBase(BaseModel):
    id_artikel: int
    judul: str
    deskripsi: str
    foto_referensi: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ArtikelCreate(BaseModel):
    judul: str
    deskripsi: str
    foto_referensi: Optional[str] = "static/placeholder.jpg"

class ArtikelUpdate(BaseModel):
    judul: Optional[str] = None
    deskripsi: Optional[str] = None
    foto_referensi: Optional[str] = None


# ============================================================
# 5. SCHEMAS UNTUK DASHBOARD STATS (Web Admin)
# ============================================================

class AdminStats(BaseModel):
    """Response untuk ringkasan angka di Dashboard Web Admin"""
    total_users: int
    total_diseases: int
    total_scans: int