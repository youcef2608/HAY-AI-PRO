import subprocess
import sys

def run_script(script_name, description):
    print(f"\n{'='*40}")
    print(f"🚀 جاري البدء في: {description}")
    print(f"{'='*40}\n")
    
    try:
        subprocess.run([sys.executable, f"h:\\HAY-AI-PRO\\{script_name}"], check=True)
    except subprocess.CalledProcessError:
        print(f"\n❌ حدث خطأ أثناء تشغيل {script_name}. يرجى التحقق من الأكواد.")
        sys.exit(1)

if __name__ == "__main__":
    # تشغيل دورة حياة الذكاء الاصطناعي بالكامل
    run_script("prepare_dataset.py", "جمع الأكواد والملفات (تغذية العقل)")
    run_script("my_custom_gpt.py", "عملية التدريب العميق (The Training)")
    run_script("vscode_ai_server.py", "تشغيل خادم VS Code")