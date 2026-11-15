import json, os, sqlite3, threading, urllib.request, tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

VERSION="1.1.0"
DATA=Path(os.getenv("APPDATA",str(Path.home())))/"Kolobok"
DATA.mkdir(parents=True,exist_ok=True)
DB=DATA/"kolobok.sqlite3"; CFG=DATA/"settings.json"

def connect():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.executescript("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,role TEXT,body TEXT,created TEXT); CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY,title TEXT,body TEXT,created TEXT);")
 c.commit(); return c

class Kolobok(tk.Tk):
 def __init__(self):
  super().__init__(); self.title("Колобок · LabokUS 1.1.0"); self.geometry("920x650"); self.configure(bg="#111827")
  self.cfg=self.load(); self.tabs=ttk.Notebook(self); self.tabs.pack(fill="both",expand=True,padx=12,pady=12)
  f=ttk.Frame(self.tabs); self.tabs.add(f,text="Ассистент"); self.log=tk.Text(f,bg="#1f2937",fg="white",wrap="word"); self.log.pack(fill="both",expand=True)
  bar=ttk.Frame(f); bar.pack(fill="x"); self.entry=tk.Text(bar,height=3); self.entry.pack(side="left",fill="x",expand=True); ttk.Button(bar,text="Отправить",command=self.send).pack(side="right")
  n=ttk.Frame(self.tabs); self.tabs.add(n,text="Память"); self.notes=tk.Listbox(n); self.notes.pack(fill="both",expand=True); ttk.Button(n,text="Добавить заметку",command=self.add_note).pack(anchor="e")
  s=ttk.Frame(self.tabs); self.tabs.add(s,text="Подключение")
  for label,key in [("API URL","base_url"),("Модель","model"),("API key","api_key")]:
   ttk.Label(s,text=label).pack(anchor="w"); v=tk.StringVar(value=self.cfg.get(key,"")); setattr(self,key,v); ttk.Entry(s,textvariable=v,width=70,show="*" if key=="api_key" else "").pack(anchor="w",pady=3)
  ttk.Button(s,text="Сохранить",command=self.save).pack(anchor="w",pady=10)
  self.history()
 def load(self):
  try:return json.loads(CFG.read_text("utf-8"))
  except:return {"base_url":"https://api.openai.com/v1","model":"gpt-4o-mini","api_key":""}
 def save(self):
  self.cfg={"base_url":self.base_url.get(),"model":self.model.get(),"api_key":self.api_key.get()}; CFG.write_text(json.dumps(self.cfg),encoding="utf-8"); messagebox.showinfo("Колобок","Сохранено")
 def history(self):
  c=connect()
  for r in c.execute("SELECT role,body FROM messages ORDER BY id"):self.log.insert("end",("Вы: " if r["role"]=="user" else "Колобок: ")+r["body"]+"\n\n")
  c.close()
 def send(self):
  q=self.entry.get("1.0","end").strip()
  if not q:return
  self.entry.delete("1.0","end"); self.log.insert("end","Вы: "+q+"\n")
  c=connect(); c.execute("INSERT INTO messages(role,body,created) VALUES(?,?,?)",("user",q,datetime.now().isoformat())); c.commit(); c.close()
  threading.Thread(target=self.ask,args=(q,),daemon=True).start()
 def ask(self,q):
  try:
   if not self.cfg.get("api_key"):raise RuntimeError("Добавь API key в настройках.")
   data=json.dumps({"model":self.cfg["model"],"messages":[{"role":"system","content":"Ты Колобок, персональный помощник. Отвечай по-русски."},{"role":"user","content":q}]}).encode()
   req=urllib.request.Request(self.cfg["base_url"].rstrip("/")+"/chat/completions",data=data,headers={"Authorization":"Bearer "+self.cfg["api_key"],"Content-Type":"application/json"})
   with urllib.request.urlopen(req,timeout=60) as r:answer=json.loads(r.read())["choices"][0]["message"]["content"]
  except Exception as e:answer="Ошибка API: "+str(e)
  c=connect(); c.execute("INSERT INTO messages(role,body,created) VALUES(?,?,?)",("assistant",answer,datetime.now().isoformat())); c.commit(); c.close()
  self.after(0,lambda:self.log.insert("end","Колобок: "+answer+"\n\n"))
 def add_note(self):
  title=simpledialog.askstring("Память","Название:",parent=self); body=simpledialog.askstring("Память","Содержание:",parent=self)
  if title and body:
   c=connect(); c.execute("INSERT INTO notes(title,body,created) VALUES(?,?,?)",(title,body,datetime.now().isoformat())); c.commit(); c.close(); self.notes.insert("end",title)

if __name__=="__main__":Kolobok().mainloop()