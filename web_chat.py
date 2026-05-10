from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import httpx

app = FastAPI(title="HAY-AI Web")

# واجهة الموقع (HTML & CSS & JavaScript)
html_content = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>محادثة Ollama | تطبيق الويب</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #fff; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        #chat-container { width: 100%; max-width: 800px; }
        #chat { height: 500px; overflow-y: auto; background-color: #2d2d2d; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .user { color: #569cd6; font-weight: bold; margin-bottom: 5px; }
        .ai { color: #4ec9b0; margin-bottom: 15px; line-height: 1.6;}
        hr { border: 0; height: 1px; background-image: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0)); }
        .input-area { display: flex; gap: 10px; }
        input { flex: 1; padding: 15px; font-size: 16px; border-radius: 8px; border: none; background-color: #3d3d3d; color: white; }
        button { padding: 15px 30px; font-size: 16px; background-color: #0e639c; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #1177bb; }
    </style>
</head>
<body>
    <div id="chat-container">
        <h2>محادثة الذكاء الاصطناعي عبر الويب 🌐</h2>
        <div id="chat"></div>
        <div class="input-area">
            <input type="text" id="msg" placeholder="اكتب رسالتك هنا..." onkeypress="if(event.key === 'Enter') send()">
            <button onclick="send()">إرسال 🚀</button>
        </div>
    </div>

    <script>
        async function send() {
            const input = document.getElementById("msg");
            const text = input.value.trim();
            if (!text) return;
            
            const chat = document.getElementById("chat");
            chat.innerHTML += `<div class="user">👤 أنت: <br><span style="color: #d4d4d4; font-weight: normal;">${text}</span></div>`;
            input.value = "";
            
            chat.innerHTML += `<div id="loading" style="color:gray; font-style: italic;">جاري التفكير... 🧠</div>`;
            chat.scrollTop = chat.scrollHeight;

            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt: text })
                });
                
                document.getElementById("loading").remove();
                const data = await response.json();
                chat.innerHTML += `<div class="ai">🤖 الذكاء الاصطناعي:<br><span style="color: #d4d4d4;">${data.reply.replace(/\\n/g, '<br>')}</span></div><hr>`;
            } catch (error) {
                document.getElementById("loading").remove();
                chat.innerHTML += `<div style="color: red;">❌ حدث خطأ في الاتصال بالسيرفر.</div><hr>`;
            }
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_home():
    return html_content

class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    # الاتصال بـ Ollama الموجود على السيرفر
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "http://127.0.0.1:11434/api/chat",
                json={
                    "model": "qwen2.5-coder:7b",
                    "messages": [{"role": "user", "content": req.prompt}],
                    "stream": False
                },
                timeout=120.0
            )
            data = res.json()
            return {"reply": data["message"]["content"]}
    except Exception as e:
        return {"reply": f"❌ خطأ داخلي: {str(e)}"}

if __name__ == "__main__":
    # تشغيل الموقع على المنفذ 80 (المنفذ الافتراضي للمواقع)
    # لجعله متاحاً للإنترنت، نستخدم 0.0.0.0
    uvicorn.run(app, host="0.0.0.0", port=80)