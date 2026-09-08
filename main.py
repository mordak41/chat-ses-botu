import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
from fastapi.responses import Response

app = FastAPI()

# Tüm tarayıcı ve köprü kısıtlamalarını tamamen kaldıran CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. HER TÜRLÜ PARAMETRE UYUMSUZLUĞUNU ÇÖZEN GÜVENLİ CHAT ENTEGRASYONU
@app.post("/chat")
async def chat_with_gemini(data: dict):
    # Arayüzden gelebilecek hem ingilizce hem türkçe parametre anahtarlarını garantiye alıyoruz
    mesaj = data.get("message") or data.get("mesaj")
    api_key = data.get("api_key") or data.get("apiKey")
    
    if not mesaj or not api_key:
        raise HTTPException(status_code=400, detail="Missing parameter: message or api_key")
    
    try:
        # API anahtarının başındaki ve sonundaki boşlukları temizleyerek güvenle kuruyoruz
        genai.configure(api_key=str(api_key).strip())
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(str(mesaj))
        
        if response and response.text:
            return {"reply": response.text}
        else:
            raise HTTPException(status_code=500, detail="Gemini returned empty response.")
            
    except Exception as e:
        print("Gemini Backend Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# 2. 10 BAYAN SES PARAMETRESİNİ ÇALIŞTIRAN TTS ENTEGRASYONU
@app.get("/tts")
async def text_to_speech(text: str, rate: str = "+0%", pitch: str = "+0Hz"):
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    try:
        communicate = edge_tts.Communicate(text, "tr-TR-EmelNeural", rate=rate, pitch=pitch)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
                
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
