import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import httpx

app = FastAPI(title="HAY-AI PRO | Premium Cloud")

# واجهة الموقع الأسطورية (Premium Design + Image Support)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAY-AI PRO | مساعدك الذكي</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #6c5ce7; --bg: #050505; --text: #e0e0e0; }
        body { font-family: 'Cairo', sans-serif; background: radial-gradient(circle at top right, #1a1a2e, #050505); color: var(--text); margin: 0; height: 100vh; display: flex; justify-content: center; align-items: center; }
        .container { width: 95%; max-width: 900px; height: 85vh; background: rgba(255,255,255,0.05); backdrop-filter: blur(15px); border-radius: 24px; display: flex; flex-direction: column; box-shadow: 0 20px 50px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); }
        header { padding: 20px 30px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; }
        #chat-area { flex: 1; overflow-y: auto; padding: 25px; display: flex; flex-direction: column; gap: 15px; }
        .msg { max-width: 80%; padding: 12px 18px; border-radius: 18px; line-height: 1.6; }
        .user { align-self: flex-end; background: var(--primary); box-shadow: 0 4px 15px rgba(108,92,231,0.4); }
        .ai { align-self: flex-start; background: rgba(255,255,255,0.08); }
        .input-container { padding: 20px 30px; display: flex; gap: 12px; }
        input { flex: 1; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; padding: 14px 20px; color: white; outline: none; }
        button { background: var(--primary); color: white; border: none; border-radius: 14px; padding: 0 25px; cursor: pointer; font-weight: bold; }
        pre { background: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>HAY-AI PRO ⚡</h1>
            <button onclick="copyAPI()" id="copyBtn" style="background:rgba(255,255,255,0.1); color:white; border:none; padding:5px 10px; border-radius:8px; cursor:pointer;">نسخ رابط API 📋</button>
        </header>
        <div id="chat-area">
            <div class="msg ai">أهلاً بك! أنا HAY-AI PRO. اطلب مني كتابة كود أو رسم صورة وسأفعل ذلك فوراً! 🚀</div>
        </div>
        <div class="input-container">
            <input type="text" id="userInput" placeholder="اكتب سؤالك هنا..." onkeypress="if(event.key==='Enter') send()">
            <button onclick="send()">إرسال</button>
        </div>
    </div>
    <script>
        const chatArea = document.getElementById('chat-area');
        function copyAPI() {
            navigator.clipboard.writeText(window.location.origin + "/v1");
            document.getElementById('copyBtn').innerText = "تم النسخ! ✅";
            setTimeout(() => { document.getElementById('copyBtn').innerText = "نسخ رابط API 📋"; }, 2000);
        }
        async function send() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if(!text) return;
            appendMsg('user', text);
            input.value = '';
            const loading = appendMsg('ai', 'جاري التفكير... ✨');
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: text})
                });
                const data = await res.json();
                loading.innerHTML = formatMsg(data.reply);
            } catch (e) { loading.innerHTML = '❌ خطأ في الاتصال.'; }
            chatArea.scrollTop = chatArea.scrollHeight;
        }
        function formatMsg(text) {
            text = text.replace(/\\!\\[image\\]\\((.*?)\\)/g, '<br><img src="$1" style="width:100%; border-radius:10px;"><br>');
            text = text.replace(/```([\\s\\S]*?)```/g, '<pre><code>$1</code></pre>');
            return text.replace(/\\n/g, '<br>');
        }
        function appendMsg(role, text) {
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            div.innerHTML = text;
            chatArea.appendChild(div);
            chatArea.scrollTop = chatArea.scrollHeight;
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
    api_key = os.environ.get("GROQ_API_KEY")
    async with httpx.AsyncClient() as client:
        try:
            system_prompt = "You are HAY-AI PRO, a world-class AI assistant. You can write code and GENERATE IMAGES using markdown: ![image](https://pollinations.ai/p/DESCRIPTION?width=1024&height=1024). Answer in Arabic."
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": req.prompt}],
                    "temperature": 0.7
                },
                timeout=60.0
            )
            data = response.json()
            return {"reply": data["choices"][0]["message"]["content"]}
        except Exception as e: return {"reply": f"خطأ: {str(e)}"}

@app.post("/v1/chat/completions")
async def v1_chat(req: Request):
    body = await req.json()
    api_key = os.environ.get("GROQ_API_KEY")
    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=body, timeout=60.0)
        return res.json()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
