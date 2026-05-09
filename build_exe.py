import subprocess
import sys
import os
import shutil
import zipfile

print("🚀 جاري تجهيز الذكاء الاصطناعي كبرنامج تنفيذي (.exe)...")

# 1. تثبيت أداة التحويل PyInstaller
subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

# 2. تحويل البرنامج
# ملاحظة: نستخدم --copy-metadata لتجنب مشاكل مكتبة tiktoken عند التجميع
command = [
    sys.executable, "-m", "PyInstaller", "--onefile", 
    "--copy-metadata", "tiktoken", 
    "--name", "Crazy_AI", 
    "h:\\HAY-AI-PRO\\test_crazy_ai.py"
]
subprocess.run(command, check=True)

print("\n📦 جاري تجهيز ملف الرفع (ZIP) لـ GitHub...")
dist_dir = "h:\\HAY-AI-PRO\\dist"
exe_path = os.path.join(dist_dir, "Crazy_AI.exe")
brain_source = "h:\\HAY-AI-PRO\\my_own_brain.pth"
brain_dest = os.path.join(dist_dir, "my_own_brain.pth")
zip_path = "h:\\HAY-AI-PRO\\Crazy_AI_Release.zip"

# نسخ العقل إلى مجلد dist ليكون بجانب البرنامج
if os.path.exists(brain_source):
    shutil.copy(brain_source, brain_dest)

# ضغط الملفين معاً لسهولة الرفع
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    if os.path.exists(exe_path):
        zipf.write(exe_path, "Crazy_AI.exe")
    if os.path.exists(brain_dest):
        zipf.write(brain_dest, "my_own_brain.pth")

print(f"\n✅ تم الانتهاء بنجاح! الملف جاهز للرفع: {zip_path}")
print("🚀 اذهب إلى GitHub وارفع ملف Crazy_AI_Release.zip ليحمله الجميع!")