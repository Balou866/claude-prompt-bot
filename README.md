# Claude Prompt Bot

Bot automatique pour envoyer un message quotidien à Claude.ai.

## Configuration

1. Récupérer votre session key Claude.ai :
   - Connectez-vous à claude.ai
   - F12 > Application > Cookies > claude.ai
   - Copiez la valeur du cookie `sessionKey`

2. Configurez les variables d'environnement :
   - `CLAUDE_SESSION_KEY` : votre session key
   - `MESSAGE` : le message à envoyer (défaut: "quelle est la météo du jour à Marseille ?")

## Utilisation avec Docker

```bash
docker build -t claude-prompt-bot .
docker run -d \
  -e CLAUDE_SESSION_KEY=votre_session_key \
  -e MESSAGE="quelle est la météo du jour à Marseille ?" \
  -v claude_logs:/app/logs \
  --name claude-bot \
  claude-prompt-bot
```

## Fonctionnement

- Envoi automatique à 5h30 (heure française) tous les jours
- Crée une nouvelle conversation pour chaque message
- Logs disponibles dans `/app/logs/claude.log`

## Notes

- La session key doit être renouvelée périodiquement
- Le container redémarre automatiquement en cas d'erreur
