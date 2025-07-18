# Claude Auto Message Bot

Bot automatique pour envoyer des messages programmés à Claude.ai via Docker.

## 🚀 Utilisation rapide

1. **Copie le contenu de `docker-compose-custom.yml`** dans ton stack Portainer
2. **Modifie ta session key** : remplace `coller_votre_session_key` par ta vraie clé
3. **Personnalise les horaires** dans la section `environment` :
   ```yaml
   - SCHEDULE_1=06:00|quelle est la météo du jour à Marseille ?
   - SCHEDULE_2=11:00|peux-tu me donner un résumé des actualités importantes ?
   - SCHEDULE_3=16:00|quels sont les événements importants de cette fin de journée ?
   ```

## ⚙️ Configuration

### Format des horaires
```yaml
- SCHEDULE_X=HH:MM|ton message ici
```

### Ajouter d'autres horaires
Décommente et modifie selon tes besoins :
```yaml
- SCHEDULE_4=20:00|bonne soirée ! comment s'est passée ta journée ?
- SCHEDULE_5=22:00|bonne nuit ! à demain
```

## 📁 Fichiers disponibles

- `docker-compose-custom.yml` - **Version recommandée** (horaires personnalisables)
- `docker-compose-multi.yml` - Version fixe (6h, 11h, 16h)
- `docker-compose-original.yml` - Version originale (1 seul horaire)

## 🔑 Session Key

Récupère ta session key depuis les cookies de Claude.ai dans ton navigateur (cookie `sessionKey`).

## 📝 Titres des conversations

Les conversations auront des titres sympas :
- **6h** → "Chat Matin 6h - 18/07"  
- **16h** → "Chat Après-midi 16h - 18/07"
- **20h** → "Chat Soirée 20h - 18/07"