import sys
from sqlalchemy import text
from app.database import SessionLocal, engine
from app.models import Penyakit, Rekomendasi, RiwayatDeteksi
from app.main import startup_seeding

db = SessionLocal()
try:
    print("Mereset tabel riwayat_deteksi, Rekomendasi, dan Penyakit...")
    db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    db.execute(text("TRUNCATE TABLE riwayat_deteksi;"))
    db.execute(text("TRUNCATE TABLE rekomendasi;"))
    db.execute(text("TRUNCATE TABLE penyakit;"))
    db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    db.commit()
    print("Tabel berhasil direset.")
    
    print("Menjalankan ulang seeding...")
    startup_seeding()
    print("Database berhasil di-update dengan data terbaru!")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
