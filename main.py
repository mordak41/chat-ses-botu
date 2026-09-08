import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import edge_tts

app = FastAPI()

# Tarayıcı iletişim kilitlerini tamamen açan CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. ENGELLERİ AŞAN GÜVENLİ GEMİNİ CHAT BAĞLANTISI (Düzeltilen Kısım)
@app.post("/chat")
async def chat_with_gemini(data: dict):
    mesaj = data.get("message")
    api_key = data.get("api_key")
    
    if not mesaj or not api_key:
        raise HTTPException(status_code=400, detail="Mesaj veya API anahtarı eksik.")
    
    try:
        # Google API Yapılandırması ve En Kararlı Başlatma Metodu
        genai.configure(api_key=api_key.strip())
        
        # En sorunsuz çalışan model tanımı
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Metin üretimi tetikleniyor
        response = model.generate_content(mesaj)
        
        if response and response.text:
            return {"reply": response.text}
        else:
            raise HTTPException(status_code=500, detail="Gemini boş yanıt döndürdü.")
            
    except Exception as e:
        # Hatayı Render loglarına basması için genişletiyoruz
        print("Gemini Motor Hatası:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# 2. MEVCUT ÇALIŞAN SESLENDİRME ALTYAPINIZ (EDGE TTS)
@app.get("/tts")
async def text_to_speech(text: str, rate: str = "+0%", pitch: str = "+0Hz"):
    if not text:
        raise HTTPException(status_code=400, detail="Metin boş olamaz.")
    try:
        # Sizin projenizdeki tr-TR-EmelNeural temel ses motoru
        communicate = edge_tts.Communicate(text, "tr-TR-EmelNeural", rate=rate, pitch=pitch)
        
        # Sesi anlık olarak belleğe akıtıp tarayıcıya yolluyoruz
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
                
        from fastapi.responses import Response
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
