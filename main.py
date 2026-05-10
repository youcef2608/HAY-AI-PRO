import sys
import os
import threading
import asyncio
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import httpx

# استيراد المكونات التي بنيناها
from hay_ai.config import Config
from hay_ai.agent import Agent
from hay_ai.server import app
import uvicorn

class HayAiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HAY-AI PRO | مساعد البرمجة الذكي")
        self.root.geometry("900x700")
        self.root.configure(bg="#0a0a0f")
        
        self.config = Config()
        self.agent = Agent(self.config)
        self.is_server_running = False

        self.setup_styles()
        self.create_widgets()
        
        # تشغيل الخادم والتحقق من Ollama في الخلفية
        threading.Thread(target=self.start_backend, daemon=True).start()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#0a0a0f")
        style.configure("Vertical.TScrollbar", background="#1a1a2e", bordercolor="#0a0a0f", arrowcolor="#6c5ce7")

    def create_widgets(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg="#12121a", width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(self.sidebar, text="🧠 HAY-AI PRO", font=("Segoe UI", 16, "bold"), bg="#12121a", fg="#a29bfe", pady=20).pack()
        
        self.status_label = tk.Label(self.sidebar, text="● جاري الفحص...", font=("Segoe UI", 10), bg="#12121a", fg="#ff9100")
        self.status_label.pack(pady=10)

        tk.Label(self.sidebar, text="مجلد العمل:", font=("Segoe UI", 9), bg="#12121a", fg="#8888aa").pack(pady=(20,0))
        self.ws_entry = tk.Entry(self.sidebar, bg="#1a1a2e", fg="white", insertbackground="white", borderwidth=0)
        self.ws_entry.pack(padx=10, pady=5, fill=tk.X)
        self.ws_entry.insert(0, os.getcwd())

        self.clear_btn = tk.Button(self.sidebar, text="🗑️ مسح المحادثة", command=self.clear_chat, bg="#1a1a2e", fg="#8888aa", relief=tk.FLAT, pady=5)
        self.clear_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)

        # Main Chat Area
        self.main_frame = tk.Frame(self.root, bg="#0a0a0f")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.chat_area = scrolledtext.ScrolledText(
            self.main_frame, bg="#0a0a0f", fg="#e8e8f0", 
            font=("Consolas", 12), borderwidth=0, padx=20, pady=20,
            insertbackground="white", state=tk.DISABLED
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        
        # Input Area
        self.input_frame = tk.Frame(self.main_frame, bg="#0a0a0f", pady=20, padx=20)
        self.input_frame.pack(fill=tk.X)
        
        self.msg_input = tk.Text(self.input_frame, height=3, bg="#12121a", fg="white", font=("Segoe UI", 12), borderwidth=1, relief=tk.FLAT, padx=10, pady=10)
        self.msg_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_input.bind("<Return>", self.handle_return)
        
        self.send_btn = tk.Button(self.input_frame, text="إرسال ➤", command=self.send_message, bg="#6c5ce7", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=20)
        self.send_btn.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        self.chat_area.tag_config("user", foreground="#569cd6", font=("Consolas", 12, "bold"))
        self.chat_area.tag_config("ai", foreground="#4ec9b0")
        self.chat_area.tag_config("system", foreground="#8888aa", font=("Consolas", 10, "italic"))
        
        self.append_msg("system", "مرحباً بك في HAY-AI PRO. جاري تجهيز العقل المحلي...\n" + "="*40 + "\n")

    def handle_return(self, event):
        if not event.state & 0x1: # No Shift
            self.send_message()
            return "break"

    def append_msg(self, role, text):
        self.chat_area.config(state=tk.NORMAL)
        if role == "user":
            self.chat_area.insert(tk.END, "👤 أنت:\n", "user")
        elif role == "ai":
            self.chat_area.insert(tk.END, "🧠 HAY-AI:\n", "ai")
        
        self.chat_area.insert(tk.END, text + "\n\n")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def clear_chat(self):
        self.agent.clear_history()
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self.append_msg("system", "تم مسح ذاكرة الجلسة.")

    def send_message(self):
        msg = self.msg_input.get("1.0", tk.END).strip()
        if not msg or self.is_server_running == False: return
        
        self.msg_input.delete("1.0", tk.END)
        self.append_msg("user", msg)
        self.send_btn.config(state=tk.DISABLED)
        
        # التفكير في Thread منفصل
        threading.Thread(target=self.run_agent, args=(msg,), daemon=True).start()

    def run_agent(self, msg):
        workspace = self.ws_entry.get()
        if workspace: self.agent.set_workspace(workspace)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # دالة لتحديث الواجهة عند استخدام الأدوات
            def on_tool(name, args):
                self.root.after(0, lambda: self.append_msg("system", f"⚡ يستخدم أداة: {name}..."))

            response = loop.run_until_complete(self.agent.run(msg, on_tool=on_tool))
            self.root.after(0, lambda: self.append_msg("ai", response))
        except Exception as e:
            self.root.after(0, lambda: self.append_msg("system", f"❌ خطأ: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))

    def start_backend(self):
        # 1. التحقق من Ollama
        try:
            r = httpx.get("http://localhost:11434/api/version", timeout=3)
            if r.status_code == 200:
                self.root.after(0, lambda: self.status_label.config(text="● Ollama متصل", fg="#00e676"))
            else:
                raise Exception()
        except:
            self.root.after(0, lambda: self.status_label.config(text="● Ollama غير مشغل!", fg="#ff5252"))
            self.root.after(0, lambda: self.append_msg("system", "⚠️ تنبيه: Ollama غير مشغل على جهازك. يرجى تشغيله أولاً."))
            return

        # 2. بدء خادم API الخاص بـ VSCode في الخلفية
        self.is_server_running = True
        self.root.after(0, lambda: self.append_msg("system", "✅ المحرك جاهز. يمكنك التحدث معي الآن!"))
        
        try:
            config = uvicorn.Config(app, host="127.0.0.1", port=1888, log_level="warning")
            server = uvicorn.Server(config)
            server.run()
        except Exception as e:
            print(f"Server error: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        os.system('chcp 65001 > nul')
    
    root = tk.Tk()
    # تحسين جودة الخطوط في ويندوز
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    app_gui = HayAiGUI(root)
    root.mainloop()
