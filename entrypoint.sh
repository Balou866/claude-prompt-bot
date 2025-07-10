#!/bin/sh

# Création des dossiers nécessaires
mkdir -p /app/logs

# Log de démarrage
echo "$(date): Claude Auto Message démarré" >> /app/logs/claude.log

# Test de connexion initial (optionnel)
if [ -n "$CLAUDE_SESSION_KEY" ]; then
    echo "$(date): Session key configurée" >> /app/logs/claude.log
else
    echo "$(date): ATTENTION: Session key manquante" >> /app/logs/claude.log
fi

# Démarrage du service cron
echo "$(date): Démarrage du cron (5h30 tous les jours)" >> /app/logs/claude.log
exec crond -f
