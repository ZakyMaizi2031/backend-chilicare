from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id_user = Column(Integer, primary_key=True, index=True)
    nama_lengkap = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(255))
    role = Column(String(20), default="petani")
    foto_profil = Column(String(255), nullable=True)

class Penyakit(Base):
    __tablename__ = "penyakit"
    id_penyakit = Column(Integer, primary_key=True, index=True)
    nama_penyakit = Column(String(50))
    gejala_visual = Column(Text)
    penyebab = Column(String(255))
    foto_referensi = Column(String(255))

    # Relasi balik: Satu penyakit memiliki satu rekomendasi (1-to-1)
    rekomendasi = relationship("Rekomendasi", back_populates="penyakit", uselist=False, cascade="all, delete")

class Rekomendasi(Base):
    __tablename__ = "rekomendasi"
    id_rekomendasi = Column(Integer, primary_key=True, index=True)
    id_penyakit = Column(Integer, ForeignKey("penyakit.id_penyakit"))
    langkah_penanganan = Column(Text)
    nama_obat = Column(String(255))

    # Relasi: Rekomendasi ini milik penyakit tertentu
    penyakit = relationship("Penyakit", back_populates="rekomendasi")

class RiwayatDeteksi(Base):
    __tablename__ = "riwayat_deteksi"
    id_riwayat = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))
    id_penyakit = Column(Integer, ForeignKey("penyakit.id_penyakit"))
    file_foto_input = Column(String(255))
    tanggal_deteksi = Column(DateTime, default=datetime.datetime.now)
    hasil_prediksi = Column(String(50))
    tingkat_akurasi = Column(Float)

class Artikel(Base):
    __tablename__ = "artikel"
    id_artikel = Column(Integer, primary_key=True, index=True)
    judul = Column(String(100))
    deskripsi = Column(Text)
    foto_referensi = Column(String(255), nullable=True)