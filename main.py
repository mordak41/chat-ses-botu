import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import edge_tts

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_with_gemini(data: dict):
    message = data.get("message")
    api_key = data.get("api_key")
    
    if not message or not api_key:
        raise HTTPException(status_code=400, detail="Required parameters missing.")
    
    try:
        genai.configure(api_key=api_key.strip())
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(message)
        
        if response and response.text:
            return {"reply": response.text}
        else:
            raise HTTPException(status_code=500, detail="Gemini returned empty text.")
            
    except Exception as e:
        print("Gemini Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

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
                
        from fastapi.responses import Response
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
