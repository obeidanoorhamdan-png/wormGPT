import os
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from g4f.client import Client

app = FastAPI(
    title="WORM Universal AI Gateway",
    version="2.0",
    description="بوابة ذكاء اصطناعي موحدة ومجانية بدون قيود"
)

# جلب مفتاح الحماية من متغيرات البيئة في Railway (الافتراضي للاختبار)
WORM_API_KEY = os.getenv("WORM_API_KEY", "123123")

# تهيئة عميل المزودين المجانيين
client = Client()

class ChatRequest(BaseModel):
    prompt: str
    model: str = "gpt-4o"  # يمكنك تغيير النموذج الافتراضي أو إرساله من الواجهة
    max_tokens: int = 1024
    temperature: float = 0.7

def verify_api_key(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="مفتاح الحماية مفقود أو غير صالح")
    token = authorization.split(" ")[1]
    if token != WORM_API_KEY:
        raise HTTPException(status_code=403, detail="مفتاح الحماية غير صحيح")
    return token

@app.get("/")
def home():
    return {"status": "online", "message": "WORM Universal Gateway is running successfully!"}

@app.post("/v1/chat")
def chat_endpoint(request: ChatRequest, token: str = Depends(verify_api_key)):
    try:
        # إرسال الطلب عبر المزودين المتاحين بدون قيود
        response = client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}],
            temperature=request.temperature
        )
        
        reply = response.choices[0].message.content
        return {
            "status": "success",
            "model_used": request.model,
            "response": reply
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الاتصال بالمزود: {str(e)}")
      
