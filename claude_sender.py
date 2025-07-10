import requests
import json
import os
import sys
from datetime import datetime

class ClaudeMessenger:
    def __init__(self):
        self.base_url = "https://claude.ai"
        self.session = requests.Session()
        self.session_key = os.getenv('CLAUDE_SESSION_KEY')
        self.message = os.getenv('MESSAGE', 'quelle est la météo du jour à Marseille ?')
        
        # Headers standard pour Claude.ai
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Referer': 'https://claude.ai/chats'
        })
        
        if self.session_key:
            self.session.cookies.set('sessionKey', self.session_key, domain='claude.ai')

    def get_organization_id(self):
        """Récupère l'ID de l'organisation"""
        try:
            response = self.session.get(f"{self.base_url}/api/organizations")
            if response.status_code == 200:
                orgs = response.json()
                return orgs[0]['uuid'] if orgs else None
        except Exception as e:
            print(f"Erreur récupération organisation: {e}")
        return None

    def create_conversation(self, org_id):
        """Crée une nouvelle conversation"""
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
                return response.json()['uuid']
        except Exception as e:
            print(f"Erreur création conversation: {e}")
        return None

    def send_message(self, org_id, conversation_id):
        """Envoie le message météo"""
        try:
            payload = {
                "prompt": self.message,
                "timezone": "Europe/Paris",
                "model": "claude-3-5-sonnet-20241022",
                "renderedContent": self.message,
                "attachments": []
            }
            
            response = self.session.post(
                f"{self.base_url}/api/organizations/{org_id}/chat_conversations/{conversation_id}/completion",
                json=payload,
                stream=True
            )
            
            if response.status_code == 200:
                print(f"✓ Message envoyé avec succès à {datetime.now()}")
                return True
            else:
                print(f"✗ Échec envoi: {response.status_code}")
                
        except Exception as e:
            print(f"Erreur envoi message: {e}")
        return False

    def run(self):
        """Exécute le processus complet"""
        print(f"🤖 Début envoi automatique - {datetime.now()}")
        
        # Vérification session
        if not self.session_key:
            print("✗ CLAUDE_SESSION_KEY manquant")
            return False
            
        # Récupération organisation
        org_id = self.get_organization_id()
        if not org_id:
            print("✗ Impossible de récupérer l'organisation")
            return False
            
        # Création conversation
        conv_id = self.create_conversation(org_id)
        if not conv_id:
            print("✗ Impossible de créer la conversation")
            return False
            
        # Envoi message
        return self.send_message(org_id, conv_id)

if __name__ == "__main__":
    messenger = ClaudeMessenger()
    success = messenger.run()
    sys.exit(0 if success else 1)
