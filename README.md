# Claude Auto Message Bot

Bot Docker qui envoie des messages programmés à Claude.ai et supprime automatiquement les conversations après un délai configurable.

## Utilisation rapide

1. Copie le `docker-compose.yml` ci-dessous dans ton stack Portainer (ou `docker-compose up -d`)
2. Remplace `CLAUDE_SESSION_KEY` par ta vraie clé (voir section **Session Key** plus bas)
3. Personnalise les `SCHEDULE_X` selon tes horaires et messages

## docker-compose.yml

```yaml
version: '3.8'

services:
  claude-bot:
    image: python:3.11-alpine
    container_name: claude-auto-message
    environment:
      - TZ=Europe/Paris
      - CLAUDE_SESSION_KEY=coller_votre_session_key

      # Horaires et messages — Format: HH:MM|message
      - SCHEDULE_1=05:00|quelle est la météo du jour à Marseille ?
      - SCHEDULE_2=10:00|peux-tu me donner un résumé des actualités importantes ?
      - SCHEDULE_3=15:00|quels sont les événements importants de cette fin de journée ?
      - SCHEDULE_4=20:00|bonne soirée ! comment s'est passée ta journée ?
      # - SCHEDULE_5=22:00|bonne nuit ! à demain

      # Délai avant suppression automatique de la conversation (en heures)
      - DELETE_DELAY_HOURS=6

      # Modèle Claude (Haiku = moins coûteux en tokens)
      - CLAUDE_MODEL=claude-haiku-4-5-20251001

    volumes:
      - claude_logs:/app/logs
    working_dir: /app
    command:
      - sh
      - -c
      - |
        apk add --no-cache curl tzdata dcron
        pip install requests beautifulsoup4
        mkdir -p /app/logs

        cat > claude_custom_scheduler.py << 'SCRIPT_END'
        import requests
        import os
        import time
        import json
        from datetime import datetime, timedelta, time as dt_time

        PENDING_FILE = "/app/logs/pending_deletions.json"

        class ClaudeCustomScheduler:
            def __init__(self):
                self.base_url = "https://claude.ai"
                self.session = requests.Session()
                self.session_key = os.getenv("CLAUDE_SESSION_KEY")
                self.delete_delay_hours = float(os.getenv("DELETE_DELAY_HOURS", "6"))
                self.schedule = self.load_schedule_from_env()
                self.session.headers.update({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Accept": "*/*",
                    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                    "Content-Type": "application/json",
                    "Origin": "https://claude.ai",
                    "Referer": "https://claude.ai/chats",
                    "anthropic-client-platform": "web_claude_ai",
                })
                if self.session_key:
                    self.session.cookies.set("sessionKey", self.session_key, domain="claude.ai")

            def load_schedule_from_env(self):
                schedule = []
                i = 1
                while True:
                    schedule_var = os.getenv(f"SCHEDULE_{i}")
                    if not schedule_var:
                        break
                    try:
                        time_str, message = schedule_var.split("|", 1)
                        hour, minute = map(int, time_str.split(":"))
                        schedule.append({
                            "time": dt_time(hour, minute),
                            "message": message,
                            "label": f"SCHEDULE_{i}"
                        })
                    except Exception as e:
                        print(f"Erreur parsing SCHEDULE_{i}: {e}")
                    i += 1
                if not schedule:
                    print("Aucun horaire configuré, utilisation des horaires par défaut")
                    schedule = [
                        {"time": dt_time(6, 0), "message": "Bonjour !", "label": "DEFAULT_1"},
                        {"time": dt_time(18, 0), "message": "Bonne soirée !", "label": "DEFAULT_2"},
                    ]
                return schedule

            def get_organization_id(self):
                try:
                    response = self.session.get(f"{self.base_url}/api/organizations", timeout=30)
                    if response.status_code == 200:
                        orgs = response.json()
                        return orgs[0]["uuid"] if orgs else None
                    print(f"/api/organizations a renvoyé {response.status_code}: {response.text[:200]}")
                except Exception as e:
                    print(f"Erreur organisation: {e}")
                return None

            def create_conversation(self, org_id, time_slot):
                try:
                    hour = time_slot.hour
                    if 5 <= hour < 12:
                        period = "Matin"
                    elif 12 <= hour < 17:
                        period = "Après-midi"
                    elif 17 <= hour < 21:
                        period = "Soirée"
                    else:
                        period = "Nuit"
                    payload = {
                        "uuid": None,
                        "name": f"Chat {period} {hour}h - {datetime.now().strftime('%d/%m')}"
                    }
                    response = self.session.post(
                        f"{self.base_url}/api/organizations/{org_id}/chat_conversations",
                        json=payload,
                        timeout=30
                    )
                    if response.status_code in (200, 201):
                        return response.json()["uuid"]
                    print(f"Création conversation HTTP {response.status_code}: {response.text[:200]}")
                except Exception as e:
                    print(f"Erreur conversation: {e}")
                return None

            def send_message(self, org_id, conversation_id, message):
                try:
                    payload = {
                        "prompt": message,
                        "parent_message_uuid": "00000000-0000-4000-8000-000000000000",
                        "timezone": os.getenv("TZ", "Europe/Paris"),
                        "locale": "fr-FR",
                        "model": os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001"),
                        "attachments": [],
                        "files": [],
                        "sync_sources": [],
                        "rendering_mode": "messages",
                    }
                    response = self.session.post(
                        f"{self.base_url}/api/organizations/{org_id}/chat_conversations/{conversation_id}/completion",
                        json=payload,
                        headers={"Accept": "text/event-stream"},
                        stream=True,
                        timeout=180,
                    )
                    if response.status_code != 200:
                        print(f"Échec envoi HTTP {response.status_code}: {response.text[:300]}")
                        return False
                    events = 0
                    completion_chars = 0
                    stop_reason = None
                    for line in response.iter_lines(decode_unicode=True):
                        if not line or not line.startswith("data: "):
                            continue
                        raw = line[6:].strip()
                        if not raw or raw == "[DONE]":
                            continue
                        try:
                            data = json.loads(raw)
                        except json.JSONDecodeError:
                            continue
                        events += 1
                        evt_type = data.get("type", "")
                        if evt_type == "completion":
                            completion_chars += len(data.get("completion", ""))
                        elif evt_type in ("message_stop", "message_limit"):
                            stop_reason = data.get("stop_reason") or evt_type
                            break
                        elif evt_type == "error":
                            print(f"Erreur stream: {data}")
                            return False
                    if events == 0:
                        print("Stream vide — inférence non déclenchée (payload/headers refusés ou quota atteint)")
                        return False
                    print(f"Message traité ({events} events, {completion_chars} chars, stop={stop_reason})")
                    return True
                except Exception as e:
                    print(f"Erreur envoi: {e}")
                    return False

            def delete_conversation(self, org_id, conversation_id):
                try:
                    response = self.session.delete(
                        f"{self.base_url}/api/organizations/{org_id}/chat_conversations/{conversation_id}",
                        timeout=30
                    )
                    if response.status_code in (200, 204):
                        print(f"Conversation {conversation_id[:8]}... supprimée")
                        return True
                    print(f"Suppression échouée HTTP {response.status_code}: {response.text[:200]}")
                except Exception as e:
                    print(f"Erreur suppression: {e}")
                return False

            def load_pending(self):
                if not os.path.exists(PENDING_FILE):
                    return []
                try:
                    with open(PENDING_FILE, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Lecture pending échouée ({e}), réinitialisation")
                    return []

            def save_pending(self, items):
                try:
                    with open(PENDING_FILE, "w", encoding="utf-8") as f:
                        json.dump(items, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Écriture pending échouée: {e}")

            def schedule_deletion(self, org_id, conv_id, label):
                delete_at = datetime.now() + timedelta(hours=self.delete_delay_hours)
                items = self.load_pending()
                items.append({
                    "org_id": org_id,
                    "conv_id": conv_id,
                    "label": label,
                    "delete_at": delete_at.isoformat(timespec="seconds"),
                })
                self.save_pending(items)
                print(f"Suppression planifiée pour {label} à {delete_at.strftime('%Y-%m-%d %H:%M:%S')} ({self.delete_delay_hours}h)")

            def process_pending_deletions(self):
                items = self.load_pending()
                if not items:
                    return
                now = datetime.now()
                remaining = []
                changed = False
                for it in items:
                    try:
                        due = datetime.fromisoformat(it["delete_at"])
                    except Exception:
                        changed = True
                        continue
                    if now >= due:
                        print(f"Échéance atteinte pour {it.get('label')} — suppression")
                        self.delete_conversation(it["org_id"], it["conv_id"])
                        changed = True
                    else:
                        remaining.append(it)
                if changed:
                    self.save_pending(remaining)

            def send_scheduled_message(self, slot):
                print(f"Envoi programmé {slot['time']} ({slot['label']}) - {datetime.now()}")
                if not self.session_key:
                    print("Session key manquante")
                    return False
                org_id = self.get_organization_id()
                if not org_id:
                    print("Organisation introuvable")
                    return False
                conv_id = self.create_conversation(org_id, slot['time'])
                if not conv_id:
                    print("Conversation impossible")
                    return False
                success = self.send_message(org_id, conv_id, slot['message'])
                if success:
                    self.schedule_deletion(org_id, conv_id, slot['label'])
                else:
                    self.delete_conversation(org_id, conv_id)
                return success

            def scheduler(self):
                print(f"Scheduler démarré (suppression différée: {self.delete_delay_hours}h)")
                print("Horaires programmés:")
                for slot in self.schedule:
                    print(f"  - {slot['time']} ({slot['label']}): {slot['message'][:60]}")
                pending_at_start = self.load_pending()
                if pending_at_start:
                    print(f"{len(pending_at_start)} suppression(s) en attente au démarrage")
                last_runs = {}
                while True:
                    now = datetime.now()
                    current_time = now.time()
                    current_date = now.date()
                    self.process_pending_deletions()
                    for slot in self.schedule:
                        last_run_key = f"{current_date}_{slot['time']}"
                        if (current_time.hour == slot['time'].hour
                                and current_time.minute == slot['time'].minute
                                and last_run_key not in last_runs):
                            print(f"Il est {current_time} - Envoi {slot['label']}")
                            success = self.send_scheduled_message(slot)
                            if success:
                                last_runs[last_run_key] = True
                                print(f"{slot['label']} envoyé (suppression dans {self.delete_delay_hours}h)")
                            else:
                                print(f"Échec envoi {slot['label']}")
                    stale = [k for k in last_runs if not k.startswith(str(current_date))]
                    for k in stale:
                        del last_runs[k]
                    if current_time.minute == 0:
                        next_slots = [s['time'] for s in self.schedule if s['time'] > current_time]
                        pending_count = len(self.load_pending())
                        next_str = min(next_slots) if next_slots else f"demain {self.schedule[0]['time']}"
                        print(f"Actif - {current_time.strftime('%H:%M')} - Prochain: {next_str} - En attente suppression: {pending_count}")
                    time.sleep(60)

        if __name__ == "__main__":
            scheduler = ClaudeCustomScheduler()
            scheduler.scheduler()
        SCRIPT_END

        python -c "import ast; ast.parse(open('claude_custom_scheduler.py').read()); print('Syntaxe OK')"
        python -u claude_custom_scheduler.py 2>&1
    restart: unless-stopped

volumes:
  claude_logs:
```

## Configuration

| Variable | Description | Exemple |
|---|---|---|
| `CLAUDE_SESSION_KEY` | Cookie `sessionKey` de claude.ai | `sk-ant-sid02-...` |
| `SCHEDULE_X` | Horaire et message (format `HH:MM\|message`) | `08:00\|Bonjour !` |
| `DELETE_DELAY_HOURS` | Délai avant suppression auto (heures) | `6` |
| `CLAUDE_MODEL` | Modèle à utiliser | voir ci-dessous |

### Modèles disponibles

| Valeur | Coût tokens | Usage |
|---|---|---|
| `claude-haiku-4-5-20251001` | Minimum | Messages simples (défaut recommandé) |
| `claude-sonnet-4-6` | Moyen | Réponses plus détaillées |
| `claude-opus-4-7` | Maximum | Tâches complexes |

## Session Key

1. Ouvre [claude.ai](https://claude.ai) dans ton navigateur et connecte-toi
2. Ouvre les DevTools (F12) → Onglet **Application** → **Cookies** → `claude.ai`
3. Copie la valeur du cookie `sessionKey`
4. Colle-la dans `CLAUDE_SESSION_KEY`

> La session key expire périodiquement — si le bot cesse de fonctionner, renouvelle-la.

## Comportement

- Chaque message crée une nouvelle conversation nommée `Chat Matin/Après-midi/Soirée/Nuit HHh - JJ/MM`
- La conversation est **automatiquement supprimée** après `DELETE_DELAY_HOURS` heures
- Si l'envoi échoue, la conversation vide est supprimée immédiatement
- Les suppressions en attente sont persistées dans `/app/logs/pending_deletions.json` et survivent aux redémarrages
