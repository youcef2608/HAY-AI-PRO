# استخدام صورة بايثون نحيفة
FROM python:3.11-slim

# تثبيت الأدوات الأساسية و Ollama
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://ollama.com/install.sh | sh

# إعداد مجلد العمل
WORKDIR /app

# نسخ الملفات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY web_chat.py .

# فتح المنفذ 7860 (المنفذ الافتراضي لـ Hugging Face)
EXPOSE 7860

# سكربت لتشغيل Ollama وتحميل النموذج ثم تشغيل الموقع
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 5\n\
ollama pull qwen2.5-coder:1.5b\n\
python web_chat.py --port 7860\n\
' > /app/start.sh && chmod +x /app/start.sh

# تشغيل السكربت
CMD ["/app/start.sh"]
