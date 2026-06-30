from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from ..services import storage

router = APIRouter(prefix="/api/artikel", tags=["Artikel"])

@router.get("/", response_model=List[schemas.ArtikelBase])
def get_all_artikel(
    search: str = Query(None, description="Cari berdasarkan judul artikel"),
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Artikel)
    if search:
        query = query.filter(models.Artikel.judul.contains(search))
    return query.all()

@router.get("/{id_artikel}", response_model=schemas.ArtikelBase)
def get_artikel_detail(id_artikel: int, db: Session = Depends(database.get_db)):
    artikel = db.query(models.Artikel).filter(models.Artikel.id_artikel == id_artikel).first()
    if not artikel:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")
    return artikel

@router.post("/", response_model=schemas.ArtikelBase)
async def create_artikel(
    judul: str = Form(...),
    deskripsi: str = Form(...),
    file_foto: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    foto_path = "static/placeholder.jpg"
    if file_foto:
        foto_path = storage.save_image(file_foto)
        foto_path = foto_path.replace("\\", "/")

    new_artikel = models.Artikel(
        judul=judul,
        deskripsi=deskripsi,
        foto_referensi=foto_path
    )
    db.add(new_artikel)
    db.commit()
    db.refresh(new_artikel)
    return new_artikel

@router.put("/{id_artikel}", response_model=schemas.ArtikelBase)
async def update_artikel(
    id_artikel: int,
    judul: str = Form(None),
    deskripsi: str = Form(None),
    file_foto: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    artikel = db.query(models.Artikel).filter(models.Artikel.id_artikel == id_artikel).first()
    if not artikel:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")
    
    if judul:
        artikel.judul = judul
    if deskripsi:
        artikel.deskripsi = deskripsi
    
    if file_foto:
        foto_path = storage.save_image(file_foto)
        artikel.foto_referensi = foto_path.replace("\\", "/")

    db.commit()
    db.refresh(artikel)
    return artikel

@router.delete("/{id_artikel}")
def delete_artikel(id_artikel: int, db: Session = Depends(database.get_db)):
    artikel = db.query(models.Artikel).filter(models.Artikel.id_artikel == id_artikel).first()
    if not artikel:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")
    
    db.delete(artikel)
    db.commit()
    return {"message": "Artikel berhasil dihapus"}
