import os
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from g4f.client import Client
import g4f

app = FastAPI(
    title="WORM Universal AI Gateway",
    version="2.2",
    description="بوابة ذكاء اصطناعي موحدة بدون قيود"
)

client = Client()

class ChatRequest(BaseModel):
    prompt: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1024
    temperature: float = 0.7

# تجاوز التحقق مؤقتاً للتأكد من عمل البوابة واستلام الرد
def verify_api_key(authorization: str = Header(None)):
    return "passed"

@app.get("/")
def home():
    return {"status": "online", "message": "WORM Universal Gateway is running perfectly!"}

@app.post("/v1/chat")
def chat_endpoint(request: ChatRequest, token: str = Depends(verify_api_key)):
    try:
        # محاولة الاتصال عبر العميل
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
        # الخطة البديلة في حال فشل العميل الأساسي
        try:
            fallback_response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=[{"role": "user", "content": request.prompt}],
                stream=False,
            )
            return {
                "status": "success",
                "model_used": "fallback-free",
                "response": fallback_response
            }
        except Exception as fallback_err:
            raise HTTPException(status_code=500, detail=f"فشل الاتصال بجميع المزودين: {str(e)} | الخطأ البديل: {str(fallback_err)}")
