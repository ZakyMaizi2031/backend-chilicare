from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..services import storage
from ..core import security
from ..core.config import settings

router = APIRouter(prefix="/api/auth", tags=["Auth"])
security_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme), db: Session = Depends(database.get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token kadaluarsa atau tidak valid")
    
    user = db.query(models.User).filter(models.User.id_user == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User tidak ditemukan")
    return user

@router.post("/login", response_model=schemas.Token)
def login(data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")
        
    if not security.verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    # Generate JWT Token
    access_token = security.create_access_token(data={"sub": str(user.id_user)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id_user": user.id_user,
            "nama_lengkap": user.nama_lengkap,
            "email": user.email,
            "role": user.role,
            "foto_profil": user.foto_profil,
        }
    }

@router.post("/register")
def register(data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Cek apakah email sudah terdaftar
    db_user = db.query(models.User).filter(models.User.email == data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar!")

    # 2. Hash password dan Buat user baru
    hashed_password = security.get_password_hash(data.password)
    new_user = models.User(
        nama_lengkap=data.nama,
        email=data.email,
        password=hashed_password, 
        role="petani",
        foto_profil=None    
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Registrasi Petani Berhasil", "user": new_user.nama_lengkap}

@router.put("/change-password")
def change_password(data: schemas.ChangePassword, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    # Verifikasi password lama
    if not security.verify_password(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Kata sandi lama salah")
    
    # Hash dan simpan password baru
    current_user.password = security.get_password_hash(data.new_password)
    db.commit()
    
    return {"message": "Kata sandi berhasil diubah"}

@router.put("/update-profile/{id_user}")
async def update_profile(id_user: int, file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    # Pastikan user hanya bisa mengupdate profilnya sendiri, atau jika dia admin
    if current_user.id_user != id_user and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Akses ditolak")

    user = db.query(models.User).filter(models.User.id_user == id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    path = storage.save_image(file)
    user.foto_profil = path
    db.commit()
    
    return {"message": "Foto profil berhasil diperbarui", "path": path}