@echo off
chcp 65001 >nul
echo ===================================================
echo 📤 جاري رفع الكود إلى GitHub...
echo ===================================================

:: إضافة جميع الملفات
git add .

:: عمل Commit
set /p commit_msg="أدخل وصفاً للتغييرات (أو اضغط Enter للوصف الافتراضي): "
if "%commit_msg%"=="" set commit_msg="Update HAY-AI PRO to v1.0.0"
git commit -m "%commit_msg%"

:: الرفع إلى الفرع الرئيسي
echo 🚀 جاري الرفع...
git push origin main

echo.
echo ✅ تم الرفع بنجاح! 
echo 🤖 سيقوم GitHub Actions الآن ببناء الـ EXE تلقائياً.
echo 🔗 اذهب إلى قسم 'Releases' في مستودعك بعد دقائق لتحميل البرنامج.

pause
