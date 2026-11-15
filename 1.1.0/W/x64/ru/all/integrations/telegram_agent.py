from __future__ import annotations
import json, os, time, urllib.parse, urllib.request
from pathlib import Path
DATA=Path(os.getenv('APPDATA',str(Path.home())))/'Kolobok'
CONFIG=DATA/'telegram.json'; SETTINGS=DATA/'settings.json'
def read(path):
 try:return json.loads(path.read_text('utf-8'))
 except Exception:return {}
def api(token,method,payload=None,timeout=40):
 req=urllib.request.Request(f'https://api.telegram.org/bot{token}/{method}',data=urllib.parse.urlencode(payload or {}).encode(),headers={'Content-Type':'application/x-www-form-urlencoded'})
 with urllib.request.urlopen(req,timeout=timeout) as r: result=json.loads(r.read().decode())
 if not result.get('ok'):raise RuntimeError(result.get('description','Telegram API error'))
 return result.get('result')
def ask_model(text):
 cfg=read(SETTINGS); key=cfg.get('api_key','').strip(); base=cfg.get('base_url','https://api.openai.com/v1').rstrip('/'); model=cfg.get('model','gpt-4o-mini')
 if not key:return 'Нейросетевой API не настроен. Добавь ключ в настройках Колобка.'
 data=json.dumps({'model':model,'messages':[{'role':'system','content':'Ты Колобок, персональный помощник. Отвечай по-русски.'},{'role':'user','content':text}]}).encode()
 req=urllib.request.Request(base+'/chat/completions',data=data,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=60) as r:return json.loads(r.read().decode())['choices'][0]['message']['content']
def main():
 cfg=read(CONFIG); settings=read(SETTINGS); token=(cfg.get('bot_token') or settings.get('telegram_token','')).strip(); allowed=set(map(int,cfg.get('allowed_user_ids',[])))
 if not token:raise SystemExit('Укажи bot_token в telegram.json или настройках. Создай бота через @BotFather.')
 offset=None; print('Kolobok Telegram bridge started. Stop with Ctrl+C.')
 while True:
  try:
   params={'timeout':30}
   if offset is not None:params['offset']=offset
   for update in api(token,'getUpdates',params,timeout=40):
    offset=update['update_id']+1; msg=update.get('message') or update.get('edited_message')
    if not msg or not msg.get('text'):continue
    uid=msg['from']['id']; chat=msg['chat']['id']
    if allowed and uid not in allowed:api(token,'sendMessage',{'chat_id':chat,'text':'Доступ не разрешён владельцем Колобка.'});continue
    try:answer=ask_model(msg['text'])
    except Exception as e:answer='Ошибка модели: '+str(e)
    for i in range(0,len(answer),3900):api(token,'sendMessage',{'chat_id':chat,'text':answer[i:i+3900]})
  except KeyboardInterrupt:break
  except Exception as e:print('Telegram polling error:',e);time.sleep(5)
if __name__=='__main__':main()