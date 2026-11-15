import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, os, json, urllib.request, threading
from pathlib import Path
from datetime import datetime

DATA=Path(os.getenv("APPDATA",str(Path.home())))/"Kolobok"
DATA.mkdir(parents=True,exist_ok=True)
DB=DATA/"kolobok.sqlite3"
CFG=DATA/"settings.json"

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, role TEXT, body TEXT, created TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, title TEXT, body TEXT, created TEXT)")
    c.commit(); return c

class Kolobok(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("Колобок — LabokUS 1.0.0"); self.geometry("950x650"); self.configure(bg="#111827")
        self.cfg=self.load_cfg(); self.style=ttk.Style(self); self.style.theme_use("clam")
        self.style.configure("TFrame",background="#111827"); self.style.configure("TLabel",background="#111827",foreground="#eef2ff")
        self.style.configure("TButton",padding=8); self.tabs=ttk.Notebook(self); self.tabs.pack(fill="both",expand=True,padx=12,pady=12)
        chat=ttk.Frame(self.tabs); self.tabs.add(chat,text="Ассистент")
        self.log=tk.Text(chat,bg="#1f2937",fg="#f9fafb",wrap="word",relief="flat"); self.log.pack(fill="both",expand=True,padx=8,pady=8)
        bar=ttk.Frame(chat); bar.pack(fill="x",padx=8,pady=8); self.entry=tk.Text(bar,height=3,bg="#1f2937",fg="white",insertbackground="white"); self.entry.pack(side="left",fill="x",expand=True)
        ttk.Button(bar,text="Отправить",command=self.send).pack(side="right",padx=8)
        mem=ttk.Frame(self.tabs); self.tabs.add(mem,text="Память")
        self.notes=tk.Listbox(mem,bg="#1f2937",fg="white"); self.notes.pack(fill="both",expand=True,padx=8,pady=8)
        ttk.Button(mem,text="Добавить заметку",command=self.add_note).pack(anchor="e",padx=8,pady=8); self.refresh_notes()
        settings=ttk.Frame(self.tabs); self.tabs.add(settings,text="Подключение")
        ttk.Label(settings,text="OpenAI-совместимый API").pack(anchor="w",padx=14,pady=14)
        self.base=tk.StringVar(value=self.cfg.get("base_url","https://api.openai.com/v1")); self.model=tk.StringVar(value=self.cfg.get("model","gpt-4o-mini")); self.key=tk.StringVar(value=self.cfg.get("api_key",""))
        for label,var,secret in [("API URL",self.base,False),("Модель",self.model,False),("API key",self.key,True)]:
            ttk.Label(settings,text=label).pack(anchor="w",padx=14); ttk.Entry(settings,textvariable=var,width=70,show="*" if secret else "").pack(anchor="w",padx=14,pady=4)
        ttk.Button(settings,text="Сохранить",command=self.save_cfg).pack(anchor="w",padx=14,pady=12)
        self.log.insert("end","Колобок запущен. Разговоры и заметки хранятся локально. Добавь API-ключ во вкладке «Подключение», чтобы подключить модель.\\n")
        self.load_history()
    def load_cfg(self):
        try:return json.loads(CFG.read_text("utf-8"))
        except:return {}
    def save_cfg(self):
        self.cfg={"base_url":self.base.get().strip(),"model":self.model.get().strip(),"api_key":self.key.get().strip()}
        CFG.write_text(json.dumps(self.cfg,ensure_ascii=False),encoding="utf-8"); messagebox.showinfo("Колобок","Настройки сохранены.")
    def load_history(self):
        c=db()
        for r in c.execute("SELECT role,body FROM messages ORDER BY id"):
            self.log.insert("end",("Вы: " if r["role"]=="user" else "Колобок: ")+r["body"]+"\\n\\n")
        c.close()
    def send(self):
        q=self.entry.get("1.0","end").strip()
        if not q:return
        self.entry.delete("1.0","end"); self.log.insert("end","\\nВы: "+q+"\\n")
        c=db(); c.execute("INSERT INTO messages(role,body,created) VALUES(?,?,?)",("user",q,datetime.now().isoformat())); c.commit(); c.close()
        if not self.cfg.get("api_key"):
            self.reply("Сообщение сохранено. Добавь API-ключ во вкладке «Подключение», чтобы я мог обратиться к нейросети."); return
        self.reply("Запрос отправляется модели…")
        threading.Thread(target=self.ask,args=(q,),daemon=True).start()
    def ask(self,q):
        try:
            p=self.cfg; data=json.dumps({"model":p["model"],"messages":[{"role":"system","content":"Ты Колобок, персональный помощник. Отвечай по-русски."},{"role":"user","content":q}]}).encode()
            req=urllib.request.Request(p["base_url"].rstrip("/")+"/chat/completions",data=data,headers={"Authorization":"Bearer "+p["api_key"],"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=60) as r: answer=json.loads(r.read())["choices"][0]["message"]["content"]
        except Exception as e: answer="Ошибка API: "+str(e)
        self.after(0,lambda:self.reply(answer))
    def reply(self,text):
        self.log.insert("end","Колобок: "+text+"\\n\\n"); self.log.see("end")
        c=db(); c.execute("INSERT INTO messages(role,body,created) VALUES(?,?,?)",("assistant",text,datetime.now().isoformat())); c.commit(); c.close()
    def refresh_notes(self):
        self.notes.delete(0,"end"); c=db()
        for r in c.execute("SELECT title FROM notes ORDER BY id DESC"):self.notes.insert("end",r["title"])
        c.close()
    def add_note(self):
        import tkinter.simpledialog as sd
        title=sd.askstring("Заметка","Название:",parent=self)
        if not title:return
        body=sd.askstring("Заметка","Содержание:",parent=self)
        if not body:return
        c=db(); c.execute("INSERT INTO notes(title,body,created) VALUES(?,?,?)",(title,body,datetime.now().isoformat())); c.commit(); c.close(); self.refresh_notes()

if __name__=="__main__": Kolobok().mainloop()