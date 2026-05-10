import subprocess
import sys
import os
import shutil
import zipfile

# Force UTF-8 output to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("🚀 جاري بناء HAY-AI PRO كبرنامج تنفيذي (.exe)...")
print()

# 1. Install PyInstaller
subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

# 2. Build exe
base = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base, "hay_ai", "static")

command = [
    sys.executable, "-m", "PyInstaller",
    "--noconsole",
    "--onefile",
    "--name", "HAY-AI-PRO",
    "--add-data", f"{static_dir};hay_ai/static",
    "--hidden-import", "hay_ai",
    "--hidden-import", "hay_ai.config",
    "--hidden-import", "hay_ai.providers",
    "--hidden-import", "hay_ai.tools",
    "--hidden-import", "hay_ai.agent",
    "--hidden-import", "hay_ai.server",
    "--hidden-import", "uvicorn.logging",
    "--hidden-import", "uvicorn.loops",
    "--hidden-import", "uvicorn.loops.auto",
    "--hidden-import", "uvicorn.protocols",
    "--hidden-import", "uvicorn.protocols.http",
    "--hidden-import", "uvicorn.protocols.http.auto",
    "--hidden-import", "uvicorn.protocols.websockets",
    "--hidden-import", "uvicorn.protocols.websockets.auto",
    "--hidden-import", "uvicorn.lifespan",
    "--hidden-import", "uvicorn.lifespan.on",
    "--hidden-import", "uvicorn.lifespan.off",
    "--collect-submodules", "uvicorn",
    "--collect-submodules", "fastapi",
    "main.py"
]
subprocess.run(command, check=True)

# 3. Package as ZIP
print("\n📦 جاري إنشاء ملف الرفع...")
dist_dir = "dist"
exe_path = os.path.join(dist_dir, "HAY-AI-PRO.exe")
zip_path = "HAY-AI-PRO-Release.zip"

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    if os.path.exists(exe_path):
        zf.write(exe_path, "HAY-AI-PRO.exe")

print(f"\n✅ تم البناء بنجاح!")
print(f"📁 EXE: {exe_path}")
print(f"📦 ZIP: {zip_path}")
print("🚀 جاهز للرفع إلى GitHub!")