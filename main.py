import os
import io
import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import google.generativeai as genai

app = FastAPI(title="Yapay Zeka 10 Bayan Sesi ve Sohbet Motoru")

# TARAYICI ENGELİNİ (CORS) SUNUCU SEVİYESİNDE TAMAMEN KALDIRAN KRİTİK AYAR
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. BAĞLANTI: Tarayıcıdan Gelen İstekleri Gemini API'ye İleten Güvenli Köprü (Proxy)
@app.post("/chat")
async def chat_with_gemini(data: dict):
    mesaj = data.get("message")
    api_key = data.get("api_key")
    
    if not mesaj or not api_key:
        raise HTTPException(status_code=400, detail="Mesaj veya API anahtarı girilmedi.")
    
    try:
        # Gelen API Anahtarı ile Google Yapay Zeka Kurulumu Yapılıyor
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # İstek asenkron iş parçacığına taşınarak bloklama önleniyor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, model.generate_content, mesaj)
        
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API Hatası: {str(e)}")

# 2. SESLENDİRME: Microsoft Edge TTS Altyapısı ile 10 Profil Üretim Motoru
@app.get("/tts")
async def text_to_speech(
    text: str = Query(..., description="Seslendirilecek metin"),
    rate: str = Query("+0%", description="Hız parametresi"),
    pitch: str = Query("+0Hz", description="Perde/Ton parametresi")
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Metin içeriği boş olamaz.")
        
    try:
        # Temel Türkçe bayan sesi üzerinden kurgu yapılıyor
        voice = "tr-TR-EmelNeural"
        
        # Edge TTS asenkron iletişim mimarisi kurgulanıyor
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        
        # Ses verisi anlık akış (stream) haline getiriliyor
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
                
        audio_stream.seek(0)
        
        # Oluşan canlı ses verisi doğrudan tarayıcıya (Audio elementine) üfleniyor
        return StreamingResponse(audio_stream, media_type="audio/mpeg")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ses Üretim Hatası: {str(e)}")

# Sunucunun boş kök adresine girildiğinde FastAPI'nin hata vermesini önleyen ufak bilgilendirme
@app.get("/")
async def root():
    return {"status": "online", "message": "Yapay Zeka 10 Bayan Ses ve Sohbet sunucusu başarıyla çalışıyor."}
