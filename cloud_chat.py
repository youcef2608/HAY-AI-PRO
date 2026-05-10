import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import httpx

app = FastAPI(title="HAY-AI Cloud")

# واجهة الموقع المتطورة
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>HAY-AI PRO | السحابي</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f0c29; background: linear-gradient(to bottom, #24243e, #302b63, #0f0c29); color: white; height: 100vh; margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        #chat-window { width: 90%; max-width: 800px; height: 70vh; background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 20px; overflow-y: auto; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.8); }
        .msg { margin-bottom: 15px; padding: 10px 15px; border-radius: 15px; max-width: 80%; line-height: 1.6; }
        .user { background: #6c5ce7; align-self: flex-end; margin-right: auto; }
        .ai { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); }
        .input-area { width: 90%; max-width: 800px; display: flex; gap: 10px; }
        input { flex: 1; padding: 15px; border-radius: 12px; border: none; background: rgba(255,255,255,0.1); color: white; outline: none; font-size: 16px; border: 1px solid rgba(255,255,255,0.1); }
        button { padding: 15px 30px; border-radius: 12px; border: none; background: #6c5ce7; color: white; cursor: pointer; font-weight: bold; transition: 0.3s; }
        button:hover { background: #a29bfe; transform: translateY(-2px); }
        h1 { margin-bottom: 10px; font-weight: 300; letter-spacing: 2px; }
    </style>
</head>
<body>
    <h1>HAY-AI PRO 🧠</h1>
    <div id="chat-window"></div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="اسألني أي شيء..." onkeypress="if(event.key==='Enter') send()">
        <button onclick="send()">إرسال 🚀</button>
    </div>

    <script>
        const chatWindow = document.getElementById('chat-window');
        async function send() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if(!text) return;

            appendMsg('user', text);
            input.value = '';

            const loading = appendMsg('ai', 'جاري التفكير... ⏳');
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: text})
                });
                const data = await res.json();
                loading.innerHTML = data.reply.replace(/\\n/g, '<br>');
            } catch (e) {
                loading.innerHTML = '❌ خطأ في الاتصال بالسيرفر السحابي.';
            }
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }

        function appendMsg(role, text) {
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            div.innerHTML = text;
            chatWindow.appendChild(div);
            chatWindow.scrollTop = chatWindow.scrollHeight;
            return div;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/chat")
async def chat(req: ChatRequest):
    # جلب المفتاح من إعدادات السيرفر السحابي
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        return {"reply": "❌ خطأ: مفتاح Groq API غير موجود في إعدادات السيرفر."}

    async with httpx.AsyncClient() as client:
        try:
            # الاتصال بمحرك Groq السحابي (أسرع ذكاء اصطناعي في العالم)
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile", # أقوى نموذج متاح مجاناً
                    "messages": [{"role": "user", "content": req.prompt}],
                    "temperature": 0.7
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                return {"reply": f"❌ خطأ من Groq: {response.text}"}
                
            data = response.json()
            return {"reply": data["choices"][0]["message"]["content"]}
            
        except Exception as e:
            return {"reply": f"❌ عذراً، حدث خطأ في الاتصال بالسحاب: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
