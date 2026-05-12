# Deployment Guide

## 1. GitHub repo (1 minúta)

```bash
# V priečinku ecoprodukt-ai-bot:
gh repo create ecoprodukt-ai-bot --public --source . --push
```

Alebo manuálne: github.com → New repo → `ecoprodukt-ai-bot` → push

## 2. Railway deploy (3 minúty)

```bash
# Otvor nový terminál v priečinku backend/
cd C:\Users\loker\Desktop\ecoprodukt-ai-bot\backend

railway login          # otvorí browser pre OAuth
railway init           # "Create new project" → pomenuj "ecoprodukt-ai-bot"
railway up             # deploy (Nixpacks auto-detects Python)
railway variables set ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
railway open           # otvorí URL
```

## 3. Frontend URL aktualizácia

Po deployi skopcíruj Railway URL (napr. `https://ecoprodukt-bot-production.up.railway.app`) a uprav v `frontend/index.html`:

```js
window.ECO_API_BASE = "https://ecoprodukt-bot-production.up.railway.app";
```

Potom commit + push → Railway auto-redeploy.

## 4. Email odpoveď

Otvor `EMAIL_ODPOVED.md`, doplň Railway URL a GitHub link, a odošli reply na email Martiny Kováčovej pred 15.5. 17:00.

---

## Environment Variables pre Railway

| Variable | Hodnota |
|----------|---------|
| `ANTHROPIC_API_KEY` | sk-ant-... (z console.anthropic.com) |
| `ODOO_URL` | (voliteľné, bez = demo mode) |
| `ODOO_DB` | (voliteľné) |
| `ODOO_USER` | (voliteľné) |
| `ODOO_PASSWORD` | (voliteľné) |

## Overenie po deploy

```bash
curl https://your-url.railway.app/health
# → {"status":"ok","service":"ecoprodukt-ai-bot"}

curl -X POST https://your-url.railway.app/api/conversation/start \
  -H "Content-Type: application/json" -d '{}'
# → {"conversation_id":"...","message":"Dobrý deň!..."}
```
