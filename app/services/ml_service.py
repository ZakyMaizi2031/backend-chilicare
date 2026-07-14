from PIL import Image
from ..core.config import settings
import os
import google.generativeai as genai

model = None

def cek_apakah_cabai(image_path):
    """
    Menggunakan Gemini Vision untuk mengecek apakah gambar adalah tanaman/daun/buah cabai.
    Mengembalikan True jika ya, False jika tidak.
    """
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print(">>> [WARNING] GEMINI_API_KEY tidak diatur. Melewati tahap Gatekeeper.")
        return True
        
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Menggunakan model gemini-2.5-flash yang ringan dan gratis
        model_gemini = genai.GenerativeModel('gemini-2.5-flash')
        
        img = Image.open(image_path)
        prompt = "Apakah gambar ini dengan jelas menampilkan tanaman cabai, daun cabai, atau buah cabai? Jawab HANYA dengan 'YA' atau 'TIDAK'."
        
        response = model_gemini.generate_content([prompt, img])
        jawaban = response.text.strip().upper()
        
        print(f">>> [GEMINI GATEKEEPER] Jawaban: {jawaban}")
        
        if "YA" in jawaban:
            return True
        return False
    except Exception as e:
        print(f">>> [GEMINI ERROR] Gagal mengecek gambar: {e}")
        # Jika API error (misal koneksi putus), biarkan lolos ke TensorFlow agar aplikasi tidak rusak total
        return True

def load_model():
    global model
    import os
    import keras
    import tensorflow as tf
    
    # Gunakan path absolut dari settings agar aman dijalankan dari direktori kerja mana pun
    model_path = settings.MODEL_PATH
    
    print(f">>> [DEBUG] Mencari model di: {model_path}")
    
    if os.path.exists(model_path):
        try:
            model = keras.models.load_model(model_path)
            print(f">>> [ML SUCCESS] Model berhasil dimuat!")
        except Exception as e:
            print(f">>> [ML ERROR] Gagal load file .keras: {e}")
    else:
        print(f">>> [ML DANGER] FILE .KERAS TIDAK DITEMUKAN!")


def run_inference(image_path):
    import numpy as np
    try:
        if model is None:
            return "Model Error", 0.0

        # 1. Load Gambar & Konversi ke RGB
        img = Image.open(image_path).convert('RGB')
        
        # 2. Resize ke 224x224 (Sesuai IMG_SIZE di Colab)
        img = img.resize((224, 224))
        
        # 3. Konversi ke Numpy Array
        img_array = np.array(img, dtype=np.float32)
        
        # 4. NORMALISASI 1./255 (Harus sama dengan ImageDataGenerator di Colab)
        img_array = img_array / 255.0
        
        # 5. Tambah Dimensi Batch
        img_array = np.expand_dims(img_array, axis=0)

        # 6. Prediksi
        predictions = model.predict(img_array, verbose=0)
        result_index = int(np.argmax(predictions[0]))
        akurasi = float(np.max(predictions[0]))
        
        # 7. URUTAN LABEL ALFABETIS (ASCII) - SESUAI FOLDER COLAB
        # Urutan: A-Z (Besar) baru a-z (kecil)
        labels = ["Antraknosa", "BercakHitamAlternaria", "BusukBuah", "Sehat"]
        
        label_hasil = labels[result_index]
        
        # 8. THRESHOLD CONFIDENCE (Jika akurasi di bawah 50%, anggap bukan cabai)
        if akurasi < 0.50:
            return "BukanCabai", akurasi
            
        return label_hasil, akurasi
        
    except Exception as e:
        print(f">>> [CRASH] ml_service error: {e}")
        return "Error", 0.0