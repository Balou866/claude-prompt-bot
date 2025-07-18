# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based automated messaging bot that sends scheduled messages to Claude.ai. The project includes multiple variants of the scheduler and a Docker-based deployment system.

## Core Architecture

### Main Components

- **ClaudeMessenger class**: Core functionality for interacting with Claude.ai API
  - Handles session management using `CLAUDE_SESSION_KEY`
  - Manages organization ID retrieval
  - Creates conversations and sends messages
  - Uses proper headers and cookie authentication

### File Structure

- `claude_scheduler.py`: Full scheduler with continuous loop checking every minute
- `claude_scheduler_fixed.py`: Simplified scheduler variant with enhanced logging
- `claude_sender.py`: One-time message sender without scheduling
- `Dockerfile`: Alpine Linux container with cron-based scheduling
- `entrypoint.sh`: Container startup script with logging
- `requirements.txt`: Python dependencies (requests, beautifulsoup4)

## Common Commands

### Running the Applications

```bash
# Run continuous scheduler
python claude_scheduler.py

# Run simplified scheduler
python claude_scheduler_fixed.py

# Send single message
python claude_sender.py
```

### Docker Deployment

```bash
# Build container
docker build -t claude-bot .

# Run with environment variables
docker run -e CLAUDE_SESSION_KEY=your_key -e MESSAGE="your message" claude-bot

# Using docker-compose (as shown in README.md)
docker-compose up -d
```

### Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

Required:
- `CLAUDE_SESSION_KEY`: Authentication session key for Claude.ai
- `MESSAGE`: Custom message to send (defaults to weather query for Marseille)

Optional:
- `TZ`: Timezone (defaults to Europe/Paris)

## API Integration

The bot interacts with Claude.ai's private API:
- Base URL: `https://claude.ai`
- Authentication: Cookie-based using sessionKey
- Endpoints used:
  - `/api/organizations` - Get organization ID
  - `/api/organizations/{org_id}/chat_conversations` - Create conversation
  - `/api/organizations/{org_id}/chat_conversations/{conv_id}/completion` - Send message

## Scheduling

- Default schedule: 5:30 AM daily (Europe/Paris timezone)
- Docker version uses cron: `30 5 * * *`
- Python schedulers use continuous loops with 60-second intervals

## Key Implementation Details

- Uses proper User-Agent headers to mimic browser requests
- Handles conversation creation for each message
- Includes retry logic and error handling
- Logs all activities with timestamps
- Prevents duplicate sends on the same day