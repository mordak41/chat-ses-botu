from fastapi import FastAPI
from fastapi.responses import FileResponse
import edge_tts
import os

app = FastAPI()

@app.get("/seslendir")
async def seslendir(metin: str, ses: str = "tr-TR-EmelNeural", hiz: str = "+0%", ton: str = "+0Hz"):
    output_file = "ses.mp3"
    
    # Android'den gelen metin, ses, hız ve ton ayarlarıyla sesi üretiyoruz
    communicate = edge_tts.Communicate(metin, ses, rate=hiz, pitch=ton)
    await communicate.save(output_file)
    
    return FileResponse(output_file, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    # Sunucuyu bilgisayarımızda lokal olarak başlatıyoruz
    uvicorn.run(app, host="0.0.0.0", port=8000)
