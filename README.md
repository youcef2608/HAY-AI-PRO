# 🧠 HAY-AI PRO

**مساعد البرمجة الذكي المحلي** - يعمل 100% على جهازك بدون إنترنت ولا مفاتيح API

## ✨ المميزات

- 🔒 **محلي 100%** - لا يحتاج إنترنت أو مفاتيح API
- 🧠 **ذكي جداً** - يستخدم نماذج AI قوية عبر Ollama
- 🛠️ **أدوات قوية** - يقرأ/يكتب الملفات، يبحث في الكود، ينفذ الأوامر
- 🎨 **واجهة جميلة** - واجهة ويب حديثة مع دعم العربية
- 🔌 **يعمل مع VSCode** - إضافة VSCode مدمجة + API متوافق مع OpenAI
- 📦 **حجم صغير** - ملف exe خفيف (~30MB)

## 🚀 التشغيل السريع

### 1. ثبّت Ollama
حمّل من: https://ollama.com/download

### 2. شغّل HAY-AI PRO
```bash
# من الكود المصدري
pip install -r requirements.txt
python main.py

# أو شغّل الـ exe مباشرة
HAY-AI-PRO.exe
```

### 3. استمتع!
- 🌐 واجهة الويب: http://127.0.0.1:1888
- 🔌 VSCode API: http://127.0.0.1:1888/v1/chat/completions

## 🔌 ربط مع VSCode

### الطريقة 1: إضافة HAY-AI المدمجة
```bash
cd vscode-extension
npm install
npx vsce package
# ثم ثبّت الملف .vsix في VSCode
```

### الطريقة 2: عبر Continue.dev
1. ثبّت إضافة [Continue](https://continue.dev) في VSCode
2. اضبط الإعدادات:
```json
{
  "models": [{
    "title": "HAY-AI PRO",
    "provider": "openai",
    "model": "qwen2.5-coder:7b",
    "apiBase": "http://127.0.0.1:1888/v1"
  }]
}
```

## 🧠 النماذج المدعومة

| النموذج | الحجم | الوصف |
|---------|-------|-------|
| qwen2.5-coder:1.5b | ~1GB | سريع وخفيف |
| qwen2.5-coder:7b | ~4GB | متوازن ومميز |
| codellama:7b | ~4GB | قوي في البرمجة |
| deepseek-coder-v2 | ~9GB | الأقوى |

```bash
# لتحميل نموذج جديد
ollama pull qwen2.5-coder:7b
```

## 📁 هيكل المشروع

```
HAY-AI-PRO/
├── main.py              # نقطة البداية
├── hay_ai/
│   ├── config.py        # إعدادات
│   ├── providers.py     # اتصال Ollama
│   ├── tools.py         # أدوات الـ Agent
│   ├── agent.py         # محرك الذكاء
│   ├── server.py        # خادم API
│   └── static/
│       └── index.html   # واجهة الويب
├── vscode-extension/    # إضافة VSCode
├── build_exe.py         # بناء exe
└── requirements.txt
```

## صنع بواسطة Youcef 🚀
