from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import os

# Import komponen internal
from .. import models, database
from ..services import storage, ml_service

# 1. Routing Fix: Gunakan prefix tanpa slash di akhir
router = APIRouter(prefix="/api/predict", tags=["Detection"])

# 2. Endpoint Utama: Gunakan path kosong "" agar URL-nya pas di /api/predict
@router.post("") 
def predict(
    id_user: int = Form(...), 
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db)
):
    """
    Endpoint untuk mendeteksi penyakit cabai.
    Proses: Simpan Gambar -> Inferensi CNN -> Simpan Riwayat -> Kirim Hasil + Rekomendasi
    """
    try:
        # --- A. VALIDASI USER ---
        user = db.query(models.User).filter(models.User.id_user == id_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="ID User tidak valid. Silakan login ulang.")

        # --- B. PENANGANAN FILE (WINDOWS COMPATIBLE) ---
        try:
            # storage.save_image memastikan folder ada & memberikan path relatif yang aman
            path_file = storage.save_image(file)
            
            # Verifikasi fisik file (Mencegah Errno 2)
            if not os.path.exists(path_file):
                raise Exception("File gagal ditulis ke penyimpanan server.")
            
            print(f">>> [DEBUG] File berhasil diproses di: {path_file}")
        except Exception as e:
            print(f">>> [ERROR STORAGE] {e}")
            raise HTTPException(status_code=500, detail=f"Gagal menyimpan gambar di server. Detail: {str(e)}")

        # --- B.5. AI GATEKEEPER (GEMINI VISION) ---
        is_cabai = ml_service.cek_apakah_cabai(path_file)
        if not is_cabai:
            # Jika bukan cabai, hapus filenya agar tidak menuhin server
            if os.path.exists(path_file):
                os.remove(path_file)
            raise HTTPException(
                status_code=400,
                detail="Sistem AI menolak gambar: Gambar yang Anda unggah bukan merupakan tanaman, daun, atau buah cabai."
            )

        # --- C. INFERENSI ML (CNN MOBILE-NET V2) ---
        try:
            # Menjalankan real inference dari ml_service.py
            label, acc = ml_service.run_inference(path_file)
        except Exception as e:
            print(f">>> [ERROR ML] {e}")
            raise HTTPException(status_code=500, detail=f"Gagal menjalankan AI: {str(e)}")

        # --- D. PENCARIAN DATA PENYAKIT & REKOMENDASI ---
        if label == "Model Error":
            raise HTTPException(
                status_code=500,
                detail="Model AI TensorFlow belum berhasil dimuat oleh server. Coba restart server."
            )
            
        if label == "BukanCabai":
            raise HTTPException(
                status_code=400,
                detail=f"Gambar yang dimasukkan sepertinya bukan daun/buah cabai. (Tingkat keyakinan: {acc*100:.1f}%)"
            )

        # Mencari data di tabel 'penyakit' berdasarkan output dari label CNN
        penyakit = db.query(models.Penyakit).filter(models.Penyakit.nama_penyakit == label).first()
        
        if not penyakit:
            # Jika ini terjadi, berarti list 'labels' di ml_service.py tidak sama dengan isi tabel MySQL
            raise HTTPException(
                status_code=404, 
                detail=f"Diagnosa '{label}' ditemukan, tapi detail penanganannya belum ada di database."
            )

        # Ambil data rekomendasi (menggunakan relationship dari models.py)
        # Kita buat default jika data rekomendasi belum diinput admin
        rekomendasi_data = {
            "langkah_penanganan": "Belum ada langkah penanganan spesifik.",
            "nama_obat": "-"
        }
        
        if penyakit.rekomendasi:
            rekomendasi_data["langkah_penanganan"] = penyakit.rekomendasi.langkah_penanganan
            rekomendasi_data["nama_obat"] = penyakit.rekomendasi.nama_obat

        # --- E. TIDAK LAGI SIMPAN LOG RIWAYAT KE MYSQL SECARA OTOMATIS ---
        # Gunakan path dengan forward slash (/) agar bisa dibuka Flutter via URL
        clean_path = path_file.replace("\\", "/")

        # --- F. RESPONSE FINAL KE FLUTTER ---
        return {
            "status": "success",
            "id_penyakit": penyakit.id_penyakit,
            "file_foto_input": clean_path,
            "label": label,
            "confidence": acc,
            "penyakit_info": {
                "nama_penyakit": penyakit.nama_penyakit,
                "gejala_visual": penyakit.gejala_visual,
                "penyebab": penyakit.penyebab,
                "foto_referensi": penyakit.foto_referensi,
                "rekomendasi": rekomendasi_data
            }
        }

    except HTTPException as he:
        # Melempar kembali error yang sudah diformat
        raise he
    except Exception as e:
        # Fallback untuk error tidak terduga
        db.rollback()
        print(f">>> [SYSTEM CRASH] {e}")
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal pada server.")