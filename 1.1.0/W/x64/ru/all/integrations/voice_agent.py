from __future__ import annotations
import json, os, uuid, urllib.request
from pathlib import Path
DATA=Path(os.getenv('APPDATA',str(Path.home())))/'Kolobok'
def speak(text):
 import pyttsx3
 engine=pyttsx3.init();engine.say(text);engine.runAndWait()
def transcribe_file(audio_path,model='whisper-1'):
 cfg=json.loads((DATA/'settings.json').read_text('utf-8'));key=cfg.get('transcription_api_key') or cfg.get('api_key')
 if not key:raise RuntimeError('Add an API key with audio transcription access.')
 boundary='----Kolobok'+uuid.uuid4().hex;path=Path(audio_path);mime='audio/wav' if path.suffix.lower()=='.wav' else 'application/octet-stream';parts=[]
 def field(name,value):parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
 field('model',model);parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\nContent-Type: {mime}\r\n\r\n'.encode()+path.read_bytes()+b'\r\n');parts.append(f'--{boundary}--\r\n'.encode())
 req=urllib.request.Request('https://api.openai.com/v1/audio/transcriptions',data=b''.join(parts),headers={'Authorization':'Bearer '+key,'Content-Type':f'multipart/form-data; boundary={boundary}'})
 with urllib.request.urlopen(req,timeout=120) as r:return json.loads(r.read().decode())['text']