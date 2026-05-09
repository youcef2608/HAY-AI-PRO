import torch
import sys
import os

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading

# استيراد هندسة العقل وأدوات التشفير من ملفك الأصلي
sys.path.append('h:\\HAY-AI-PRO')
from my_custom_gpt import MyCustomGPT, encode, decode, device

print("🚀 جاري إيقاظ العقل المجنون...")

# تهيئة الجمجمة (النموذج) وتحميل الذكريات
model = MyCustomGPT().to(device)

# تحديد مسار العقل بذكاء (ليعمل كسكربت أو كبرنامج exe جاهز في حاسوب آخر)
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
brain_path = os.path.join(base_dir, 'my_own_brain.pth')

try:
    model.load_state_dict(torch.load(brain_path, map_location=device, weights_only=True))
    print("✅ تم استرجاع ذكريات وخبرات العقل المجنون بنجاح!")
except Exception as e:
    print(f"❌ لم يتم العثور على الذكريات في المسار: {brain_path}")
    print("يرجى التأكد من وضع ملف 'my_own_brain.pth' بجانب البرنامج مباشرة!")
    # sys.exit() # تم إيقاف الخروج الفوري لعرض رسالة خطأ في الواجهة بدلاً من ذلك

model.eval() # تفعيل وضع الاختبار (لا يتعلم هنا، بل يطبق ما تعلمه فقط)

# ==========================================
# واجهة الدردشة (Chat GUI)
# ==========================================
def send_message(event=None):
    prompt = entry_box.get().strip()
    if not prompt:
        return
        
    # عرض رسالة المستخدم
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"أنت:\n{prompt}\n\n", "user")
    chat_area.insert(tk.END, "العقل المجنون يفكر... 🧠\n", "system")
    chat_area.see(tk.END)
    chat_area.config(state=tk.DISABLED)
    entry_box.delete(0, tk.END)
    
    # تشغيل التفكير في مسار منفصل (Thread) لكي لا تتجمد الواجهة
    def generate_response():
        input_ids = encode(prompt)
        if len(input_ids) == 0:
            context = torch.zeros((1, 1), dtype=torch.long, device=device)
        else:
            context = torch.tensor([input_ids], dtype=torch.long, device=device)

        with torch.no_grad():
            generated_indices = model.generate(context, max_new_tokens=300)[0].tolist()
            
        response = decode(generated_indices)
        
        # تحديث الواجهة بشكل آمن بعد انتهاء التفكير
        def update_gui():
            chat_area.config(state=tk.NORMAL)
            chat_area.insert(tk.END, f"الذكاء الاصطناعي:\n{response}\n", "ai")
            chat_area.insert(tk.END, "-"*40 + "\n\n", "system")
            chat_area.see(tk.END)
            chat_area.config(state=tk.DISABLED)
            
        root.after(0, update_gui)

    threading.Thread(target=generate_response, daemon=True).start()

# إعداد النافذة
root = tk.Tk()
root.title("العقل المجنون - دردشة الذكاء الاصطناعي")
root.geometry("700x600")
root.configure(bg="#1e1e1e") # لون داكن (Dark Mode) مناسب للمبرمجين

# منطقة الدردشة
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 12), bg="#1e1e1e", fg="#d4d4d4", padx=10, pady=10)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# ألوان النصوص لتمييز المحادثة
chat_area.tag_config("user", foreground="#569cd6", font=("Consolas", 12, "bold"))
chat_area.tag_config("ai", foreground="#4ec9b0")
chat_area.tag_config("system", foreground="#808080", font=("Consolas", 10, "italic"))

chat_area.insert(tk.END, "🔥 العقل المجنون جاهز الآن! 🔥\nاكتب بداية أي كود وسيقوم بإكماله لك...\n" + "="*40 + "\n\n", "system")
chat_area.config(state=tk.DISABLED)

# منطقة الإدخال
input_frame = tk.Frame(root, bg="#1e1e1e")
input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

entry_box = tk.Entry(input_frame, font=("Consolas", 14), bg="#2d2d2d", fg="#ffffff", insertbackground="white")
entry_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), ipady=8)
entry_box.bind("<Return>", send_message)

send_btn = tk.Button(input_frame, text="إرسال 🚀", font=("Arial", 12, "bold"), bg="#0e639c", fg="white", command=send_message, relief=tk.FLAT)
send_btn.pack(side=tk.RIGHT, ipadx=10, ipady=3)

# عرض تنبيه لو لم يجد ملف العقل عند تشغيل البرنامج
if not os.path.exists(brain_path):
    messagebox.showerror("خطأ", "لم يتم العثور على ذكريات العقل (my_own_brain.pth)\nيرجى التأكد من وجود الملف بجانب البرنامج.")

root.mainloop()