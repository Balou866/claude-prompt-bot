FROM python:3.11-alpine

# Installation des dépendances système
RUN apk add --no-cache dcron curl tzdata

# Configuration du fuseau horaire
ENV TZ=Europe/Paris

WORKDIR /app

# Copie des fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY claude_sender.py .
COPY entrypoint.sh .

# Configuration du cron
RUN echo "30 5 * * * cd /app && python claude_sender.py >> /app/logs/claude.log 2>&1" > /etc/crontabs/root

# Permissions
RUN chmod +x entrypoint.sh

# Création du dossier logs
RUN mkdir -p /app/logs

ENTRYPOINT ["./entrypoint.sh"]
