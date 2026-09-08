import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import edge_tts

app = FastAPI()

# Tarayıcı güvenlik engellerini (CORS) kökten kaldıran kritik ayar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_with_gemini(data: dict):
    mesaj = data.get("message")
    api_key = data.get("api_key")
    
    if not mesaj or not api_key:
        raise HTTPException(status_code=400, detail="Mesaj veya API anahtarı eksik.")
    
    try:
        # Google Yapay Zeka Entegrasyonu Kurulumu
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        response = model.generate_content(mesaj)
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tts")
async def text_to_speech(text: str, rate: str = "+0%", pitch: str = "+0Hz"):
    if not text:
        raise HTTPException(status_code=400, detail="Metin parametresi eksik.")
        
    try:
        # Mevcut ücretsiz Edge TTS seslendirme altyapınız
        communicate = edge_tts.Communicate(text, "tr-TR-EmelNeural", rate=rate, pitch=pitch)
        
        # Sesi anlık olarak belleğe yazıp akış (Stream) şeklinde fırlatıyoruz
        from fastapi.responses import StreamingResponse
        import io
        
        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
                
        audio_data.seek(0)
        return StreamingResponse(audio_data, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
