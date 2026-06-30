from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, database, schemas
import os

router = APIRouter(prefix="/api/history", tags=["History"])

@router.post("")
def save_history(data: schemas.RiwayatCreate, db: Session = Depends(database.get_db)):
    """Menyimpan riwayat deteksi secara manual oleh user"""
    
    # Validasi user dan penyakit
    user = db.query(models.User).filter(models.User.id_user == data.id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
        
    penyakit = db.query(models.Penyakit).filter(models.Penyakit.id_penyakit == data.id_penyakit).first()
    if not penyakit:
        raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan")

    new_riwayat = models.RiwayatDeteksi(
        id_user=data.id_user,
        id_penyakit=data.id_penyakit,
        file_foto_input=data.file_foto_input,
        hasil_prediksi=data.hasil_prediksi,
        tingkat_akurasi=data.tingkat_akurasi
    )
    
    db.add(new_riwayat)
    db.commit()
    db.refresh(new_riwayat)
    
    return {"message": "Berhasil menyimpan riwayat deteksi", "id_riwayat": new_riwayat.id_riwayat}

@router.delete("/{id_riwayat}")
def delete_history(id_riwayat: int, db: Session = Depends(database.get_db)):
    """Menghapus riwayat deteksi berdasarkan ID"""
    
    riwayat = db.query(models.RiwayatDeteksi).filter(models.RiwayatDeteksi.id_riwayat == id_riwayat).first()
    
    if not riwayat:
        raise HTTPException(status_code=404, detail="Riwayat tidak ditemukan")
        
    # Hapus file gambar jika ada agar tidak memenuhi storage
    if riwayat.file_foto_input and os.path.exists(riwayat.file_foto_input):
        try:
            os.remove(riwayat.file_foto_input)
        except Exception as e:
            print(f"Gagal menghapus file gambar: {e}")
            
    db.delete(riwayat)
    db.commit()
    
    return {"message": "Riwayat berhasil dihapus"}
