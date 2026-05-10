import tkinter as tk
from tkinter import scrolledtext
import threading
import urllib.request
import json

# إعدادات Ollama - استخدم نفس النموذج الذي قمت بتحميله في Ollama
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "qwen2.5-coder:7b" 

def send_message(event=None):
    prompt = entry_box.get().strip()
    if not prompt:
        return
        
    # عرض رسالة المستخدم
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"أنت:\n{prompt}\n\n", "user")
    chat_area.insert(tk.END, "Ollama يفكر... 🧠\n", "system")
    chat_area.see(tk.END)
    chat_area.config(state=tk.DISABLED)
    entry_box.delete(0, tk.END)
    
    # الاتصال بـ Ollama في مسار منفصل حتى لا تتجمد الواجهة
    def generate_response():
        try:
            data = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
            req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'),
                                         headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                reply = res_json['message']['content']
                
            root.after(0, update_gui, reply)
        except Exception as e:
            error_msg = f"❌ خطأ: لم أتمكن من الاتصال بـ Ollama.\nتأكد أن برنامج Ollama يعمل، وأن النموذج ({MODEL_NAME}) محمل.\nالتفاصيل: {e}"
            root.after(0, update_gui, error_msg)

    def update_gui(response_text):
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, f"Ollama ({MODEL_NAME}):\n{response_text}\n", "ai")
        chat_area.insert(tk.END, "-"*40 + "\n\n", "system")
        chat_area.see(tk.END)
        chat_area.config(state=tk.DISABLED)

    threading.Thread(target=generate_response, daemon=True).start()

# ==========================================
# تصميم الواجهة الرسومية
# ==========================================
root = tk.Tk()
root.title("محادثة Ollama المباشرة")
root.geometry("700x600")
root.configure(bg="#1e1e1e")

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 12), bg="#1e1e1e", fg="#d4d4d4", padx=10, pady=10)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

chat_area.tag_config("user", foreground="#569cd6", font=("Consolas", 12, "bold"))
chat_area.tag_config("ai", foreground="#4ec9b0")
chat_area.tag_config("system", foreground="#808080", font=("Consolas", 10, "italic"))

chat_area.insert(tk.END, f"✅ متصل بـ Ollama محلياً 100% بدون أي أدوات خارجية.\n" + "="*40 + "\n\n", "system")
chat_area.config(state=tk.DISABLED)

input_frame = tk.Frame(root, bg="#1e1e1e")
input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

entry_box = tk.Entry(input_frame, font=("Consolas", 14), bg="#2d2d2d", fg="#ffffff", insertbackground="white")
entry_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), ipady=8)
entry_box.bind("<Return>", send_message)

send_btn = tk.Button(input_frame, text="إرسال 🚀", font=("Arial", 12, "bold"), bg="#0e639c", fg="white", command=send_message, relief=tk.FLAT)
send_btn.pack(side=tk.RIGHT, ipadx=10, ipady=3)

root.mainloop()