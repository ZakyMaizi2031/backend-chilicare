from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

# Inisialisasi router dengan prefix /api/encyclopedia
router = APIRouter(prefix="/api/encyclopedia", tags=["Encyclopedia"])

# 1. ENDPOINT: MENGAMBIL SEMUA DAFTAR PENYAKIT (KATALOG)
@router.get("/", response_model=List[schemas.PenyakitBase])
def get_all_diseases(
    search: str = Query(None, description="Cari berdasarkan nama penyakit"),
    db: Session = Depends(database.get_db)
):
    """
    Mengambil semua data penyakit untuk ditampilkan di halaman utama Ensiklopedia.
    Dilengkapi fitur pencarian sederhana.
    """
    query = db.query(models.Penyakit)
    
    # Logika Pencarian: Jika ada parameter 'search', filter query-nya
    if search:
        query = query.filter(models.Penyakit.nama_penyakit.contains(search))
    
    diseases = query.all()
    return diseases

# 2. ENDPOINT: MENGAMBIL DETAIL PENYAKIT & REKOMENDASI BERDASARKAN ID
@router.get("/{id_penyakit}")
def get_disease_detail(id_penyakit: int, db: Session = Depends(database.get_db)):
    """
    Mengambil detail lengkap satu penyakit termasuk langkah penanganan (rekomendasi).
    Endpoint ini dipanggil saat petani mengklik salah satu item di Ensiklopedia.
    """
    # Mencari penyakit berdasarkan ID
    disease = db.query(models.Penyakit).filter(models.Penyakit.id_penyakit == id_penyakit).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="Data penyakit tidak ditemukan")
    
    # Secara otomatis SQLAlchemy akan menyertakan data relasi 'rekomendasi' 
    # karena kita sudah mendefinisikan relationship di models.py
    return {
        "id_penyakit": disease.id_penyakit,
        "nama_penyakit": disease.nama_penyakit,
        "gejala_visual": disease.gejala_visual,
        "penyebab": disease.penyebab,
        "foto_referensi": disease.foto_referensi,
        "penanganan": {
            "langkah_langkah": disease.rekomendasi.langkah_penanganan if disease.rekomendasi else "Belum ada data penanganan.",
            "nama_obat": disease.rekomendasi.nama_obat if disease.rekomendasi else "N/A"
        }
    }

# 3. ENDPOINT: MENGAMBIL TOTAL JENIS PENYAKIT (UNTUK WIDGET INFO)
@router.get("/count")
def count_diseases(db: Session = Depends(database.get_db)):
    """
    Mengembalikan jumlah total penyakit yang terdaftar di database.
    """
    count = db.query(models.Penyakit).count()
    return {"total_penyakit": count}    