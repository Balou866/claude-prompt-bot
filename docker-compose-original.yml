```
version: '3.8'

services:
  claude-bot:
    image: python:3.11-alpine
    container_name: claude-auto-message
    environment:
      - TZ=Europe/Paris
      - CLAUDE_SESSION_KEY=coller_votre_session_key
      - MESSAGE=quelle est la météo du jour à Marseille ?
    volumes:
      - claude_logs:/app/logs
    working_dir: /app
    command: 
      - sh
      - -c
      - |
        apk add --no-cache curl tzdata
        pip install requests
        mkdir -p /app/logs
        
        cat > claude_scheduler.py << 'SCRIPT_END'
        import requests
        import os
        import time
        import json
        from datetime import datetime, time as dt_time
        
        class ClaudeMessenger:
            def __init__(self):
                self.base_url = "https://claude.ai"
                self.session = requests.Session()
                self.session_key = os.getenv("CLAUDE_SESSION_KEY")
                self.message = os.getenv("MESSAGE", "météo du jour")
                
                self.session.headers.update({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Referer": "https://claude.ai/chats"
                })
                
                if self.session_key:
                    self.session.cookies.set("sessionKey", self.session_key, domain="claude.ai")
        
            def get_organization_id(self):
                try:
                    response = self.session.get(f"{self.base_url}/api/organizations")
                    if response.status_code == 200:
                        orgs = response.json()
                        return orgs[0]["uuid"] if orgs else None
                except Exception as e:
                    print(f"Erreur organisation: {e}")
                return None
        
            def create_conversation(self, org_id):
                try:
                    payload = {
                        "uuid": None,
                        "name": f"Météo {datetime.now().strftime('%Y-%m-%d')}"
                    }
                    response = self.session.post(
                        f"{self.base_url}/api/organizations/{org_id}/chat_conversations",
                        json=payload
                    )
                    if response.status_code == 201:
                        return response.json()["uuid"]
                except Exception as e:
                    print(f"Erreur conversation: {e}")
                return None
        
            def send_message(self, org_id, conversation_id):
                try:
                    payload = {"prompt": self.message}
                    response = self.session.post(
                        f"{self.base_url}/api/organizations/{org_id}/chat_conversations/{conversation_id}/completion",
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        print(f"✅ Message envoyé: {self.message} à {datetime.now()}")
                        return True
                    else:
                        print(f"❌ Échec envoi: {response.status_code}")
                        
                except Exception as e:
                    print(f"Erreur envoi: {e}")
                return False
        
            def send_daily_message(self):
                print(f"🤖 Début envoi automatique - {datetime.now()}")
                
                if not self.session_key:
                    print("❌ Session key manquante")
                    return False
                    
                org_id = self.get_organization_id()
                if not org_id:
                    print("❌ Organisation introuvable")
                    return False
                    
                conv_id = self.create_conversation(org_id)
                if not conv_id:
                    print("❌ Conversation impossible")
                    return False
                    
                return self.send_message(org_id, conv_id)
        
            def scheduler(self):
                target_time = dt_time(5, 30)
                last_run_date = None
                
                print(f"🕐 Scheduler démarré - envoi quotidien à {target_time}")
                print(f"🗓️ Prochaine exécution: demain {target_time} (heure française)")
                
                while True:
                    now = datetime.now()
                    current_time = now.time()
                    current_date = now.date()
                    
                    if (current_time.hour == target_time.hour and 
                        current_time.minute == target_time.minute and 
                        current_date != last_run_date):
                        
                        print(f"⏰ Il est {current_time} - Envoi du message")
                        success = self.send_daily_message()
                        
                        if success:
                            last_run_date = current_date
                            print("✅ Message envoyé - prochaine fois demain")
                        else:
                            print("❌ Échec - retry dans 1 minute")
                    
                    if current_time.minute == 0:
                        print(f"💓 Service actif - {current_time}")
                    
                    time.sleep(60)
        
        if __name__ == "__main__":
            messenger = ClaudeMessenger()
            messenger.scheduler()
        SCRIPT_END
        
        echo "✅ Script Python créé"
        echo "📝 Vérification du script..."
        ls -la claude_scheduler.py
        echo "📄 Contenu du script (premières lignes):"
        head -10 claude_scheduler.py
        echo "🔍 Test syntaxe Python..."
        python -c "import claude_scheduler; print('Import OK')" 2>&1 || echo "❌ Erreur import"
        echo "🚀 Lancement du scheduler avec debug..."
        python -u claude_scheduler.py 2>&1
    restart: unless-stopped

volumes:
  claude_logs:



