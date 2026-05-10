"""HAY-AI PRO - Entry Point"""
import sys
import os
import subprocess
import asyncio

def check_ollama():
    """Check if Ollama is installed and running."""
    print("=" * 50)
    print("🧠 HAY-AI PRO - مساعد البرمجة الذكي المحلي")
    print("=" * 50)
    print()

    # Check if ollama command exists
    try:
        r = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            print(f"✅ Ollama مثبت: {r.stdout.strip()}")
        else:
            print("❌ Ollama غير مثبت!")
            print("📥 قم بتحميله من: https://ollama.com/download")
            print()
            input("اضغط Enter بعد تثبيت Ollama...")
            return False
    except FileNotFoundError:
        print("❌ Ollama غير مثبت!")
        print("📥 قم بتحميله من: https://ollama.com/download")
        print()
        input("اضغط Enter بعد تثبيت Ollama...")
        return False
    except Exception:
        pass

    # Check if ollama is running
    import httpx
    try:
        r = httpx.get("http://localhost:11434/api/version", timeout=3)
        if r.status_code == 200:
            print("✅ Ollama يعمل!")
            return True
    except Exception:
        pass

    print("⚠️ Ollama مثبت لكن غير مشغّل. جاري التشغيل...")
    try:
        if sys.platform == "win32":
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import time
        time.sleep(3)
        print("✅ تم تشغيل Ollama!")
    except Exception as e:
        print(f"⚠️ تعذر تشغيل Ollama تلقائياً: {e}")
        print("يرجى تشغيل 'ollama serve' يدوياً في نافذة أخرى")

    return True


def check_model():
    """Check if a coding model is downloaded."""
    import httpx
    try:
        r = httpx.get("http://localhost:11434/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        if models:
            print(f"✅ النماذج المتاحة: {', '.join(models)}")
            return True
        else:
            print()
            print("⚠️ لا توجد نماذج محملة! جاري تحميل نموذج صغير وذكي...")
            print("📥 جاري تحميل qwen2.5-coder:1.5b (~1GB)...")
            subprocess.run(["ollama", "pull", "qwen2.5-coder:1.5b"])
            return True
    except Exception:
        return False


def main():
    check_ollama()
    check_model()

    from hay_ai.config import Config
    config = Config()
    
    # Auto-detect workspace
    if not config.config["agent"].get("workspace"):
        config.config["agent"]["workspace"] = os.getcwd()
        config.save()

    # Check available models and set best one
    import httpx
    try:
        r = httpx.get("http://localhost:11434/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        # Prefer coding models
        coding_models = [m for m in models if "coder" in m or "code" in m]
        if coding_models:
            config.config["model"] = coding_models[0]
        elif models:
            config.config["model"] = models[0]
        config.save()
    except Exception:
        pass

    host = config.config["server"]["host"]
    port = config.config["server"]["port"]

    print()
    print("=" * 50)
    print(f"🚀 HAY-AI PRO يعمل الآن!")
    print(f"🌐 واجهة الويب: http://{host}:{port}")
    print(f"🔌 VSCode API:  http://{host}:{port}/v1/chat/completions")
    print(f"📁 مجلد العمل:  {config.config['agent'].get('workspace', os.getcwd())}")
    print(f"🧠 النموذج:     {config.model}")
    print("=" * 50)
    print()

    import uvicorn
    uvicorn.run("hay_ai.server:app", host=host, port=port, log_level="warning")


if __name__ == "__main__":
    main()
