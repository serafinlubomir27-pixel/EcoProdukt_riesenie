# ECO PRODUKT — AI Sales Bot

Automatizovaný predajný asistent pre fotovoltické systémy. Zákazník chatuje s AI botom, ktorý zbiera kvalifikačné dáta a generuje personalizovanú ponuku — bez obchodníka.

**Live demo:** https://ecoprodukt-bot.up.railway.app  
**Architecture:** [docs/architecture.html](docs/architecture.html)

## Čo to robí

1. Odoo vytvorí lead → pošle webhook → n8n spustí AI bota
2. Zákazník dostane email s odkazom na chat
3. AI bot (Claude Haiku) vedie 7-krokový kvalifikačný rozhovor
4. PV Calculator vygeneruje personalizovanú ponuku (kWp, cena, ROI)
5. n8n aktualizuje Odoo, notifikuje tím

## Štruktúra

```
backend/
  main.py                    # FastAPI app
  routers/conversation.py    # POST /api/conversation/start, /message, GET /{id}
  routers/webhook.py         # POST /webhook/odoo/new-lead
  services/ai_service.py     # Claude API + tool use
  services/pv_calculator.py  # Výpočet systému, ROI, úspora
  services/odoo_service.py   # Odoo XML-RPC klient (demo mode ak bez env vars)
  models/conversation.py     # Pydantic modely
  data/pv_knowledge.py       # Produktový katalóg, system prompt
frontend/
  index.html                 # Demo stránka
  chat.js                    # Vanilla JS chat widget
  styles.css                 # Styling
n8n/
  ecoprodukt-sales-automation.json   # n8n workflow export (importovateľný)
docs/
  architecture.html          # Interaktívny architecture diagram
```

## Lokálny development

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Vyplň ANTHROPIC_API_KEY v .env
uvicorn main:app --reload
```

API beží na http://localhost:8000  
Frontend otvoriť: `frontend/index.html` v prehliadači

## API Endpoints

| Method | Path | Popis |
|--------|------|-------|
| POST | `/api/conversation/start` | Začni novú konverzáciu |
| POST | `/api/conversation/{id}/message` | Pošli správu |
| GET | `/api/conversation/{id}` | Stav konverzácie |
| POST | `/webhook/odoo/new-lead` | Odoo webhook trigger |
| GET | `/health` | Health check |

## Environment Variables

```
ANTHROPIC_API_KEY=sk-ant-...       # Povinné
ODOO_URL=https://your-odoo.com     # Voliteľné (bez nich = demo mode)
ODOO_DB=production
ODOO_USER=admin
ODOO_PASSWORD=secret
```

## Deployment na Railway

```bash
railway login
railway init
railway up
railway variables set ANTHROPIC_API_KEY=sk-ant-...
```

## n8n Import

1. Otvor n8n Cloud → New Workflow → Import from file
2. Vyber `n8n/ecoprodukt-sales-automation.json`
3. Nastav environment variables: `ECO_BOT_API_URL`, `ECO_BOT_FRONTEND_URL`
4. Prepoj Gmail credentials
5. Aktivuj workflow
