import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import torch
import tiktoken
import sys

# استيراد هندسة العقل الخاص بك الذي صنعته من الصفر
sys.path.append('h:\\HAY-AI-PRO')
from my_custom_gpt import MyCustomGPT, device

# 1. إعداد السيرفر المحلي
app = FastAPI(title="My Custom VS Code AI Assistant")

# 2. تحميل عقل المبرمج (النموذج الخاص بك)
print("جاري تحميل العقل الذي قمت بصناعته وتدريبه بنفسك...")

# استخدام نفس قاموس الكلمات الاحترافي
enc = tiktoken.get_encoding("gpt2")
encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
decode = lambda l: enc.decode(l)

# تحميل الأوزان
model = MyCustomGPT().to(device)
model.load_state_dict(torch.load('h:\\HAY-AI-PRO\\my_own_brain.pth', map_location=device, weights_only=True))
model.eval() # وضع الاختبار

print("تم تحميل نموذجك الخاص بنجاح! السيرفر جاهز للربط مع VS Code 🚀")

# 3. هيكل الطلب القادم من VS Code (نصممه ليكون متوافقاً مع معايير OpenAI)
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    max_tokens: int = 150

# 4. نقطة الاتصال (Endpoint) التي سيكلمها VS Code
@app.post("/v1/chat/completions")
async def generate_code(req: ChatRequest):
    # استخراج السؤال الأخير من المستخدم
    prompt = req.messages[-1].content
    
    # تحويل النص إلى أرقام (التشفير الخاص بك)
    input_ids = encode(prompt)
    context = torch.tensor([input_ids], dtype=torch.long, device=device)
    
    # التفكير وكتابة الكود بناءً على ما تعلمه من أكوادك
    with torch.no_grad():
        generated_indices = model.generate(context, max_new_tokens=req.max_tokens)[0].tolist()
    
    # تحويل الأرقام إلى نص
    generated_text = decode(generated_indices)
    
    # استخراج الإجابة فقط (بدون السؤال الأصلي)
    answer = generated_text[len(prompt):]

    # إرجاع النتيجة بصيغة يفهمها VS Code
    return {"choices": [{"message": {"role": "assistant", "content": answer}}]}

# 5. تشغيل السيرفر
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)