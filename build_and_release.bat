@echo off
chcp 65001 >nul
echo ===================================================
echo 🚀 جاري بناء HAY-AI PRO وتحويله إلى EXE...
echo ===================================================

:: التأكد من تثبيت المكتبات
python -m pip install -r requirements.txt pyinstaller

:: تشغيل سكربت البناء
python build_exe.py

echo.
if exist dist\HAY-AI-PRO.exe (
    echo ✅ تم إنشاء الملف بنجاح في مجلد dist
    echo 📦 اسم الملف: HAY-AI-PRO.exe
) else (
    echo ❌ فشل عملية البناء. تأكد من تثبيت Python بشكل صحيح.
)

pause
