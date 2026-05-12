# Automatizácia predajného procesu FV systémov — ECO PRODUKT

**Vypracoval:** Ľubomír Serafín  
**Dátum:** Máj 2026  
**Zadanie:** Navrhnúť a implementovať riešenie, ktoré umožní zákazníkovi objednať fotovoltický systém na kľúč bez zásahu obchodníka, iba pomocou AI bota (termín spustenia: august 2026)

---

## Problém, ktorý riešime

Predaj FV systémov je dnes závislý na obchodníkovi: zákazník vypíše formulár → čaká na spätné volanie → dohodne stretnutie → dostane ponuku. Tento proces trvá dni až týždne a vyžaduje pracovný čas skúsených ľudí na rutinné úkony (kvalifikácia, kalkulácia, tvorba ponuky).

**Cieľ:** Celý tento proces skrátiť na 5 minút a zautomatizovať od prvého kontaktu po záväznú ponuku.

---

## Riešenie

Postavil som funkčný prototyp systému pozostávajúceho z troch prepojených vrstiev:

### 1. AI Sales Bot (živý demo)

FastAPI backend s Claude AI, ktorý vedie zákazníka cez 7-krokový kvalifikačný dialóg:

- Typ nehnuteľnosti → spotreba elektriny → parametre strechy → lokalita → budget → termín → kontakt

Po zozbieraní dát **PV Calculator okamžite vypočíta** optimálny výkon systému, cenu, ročnú úsporu a návratnosť investície. Zákazník dostane konkrétnu ponuku — nie "zavoláme vám".

**Ukážka výstupu:**
```
⚡ Výkon systému: 5 kWp (13 panelov)
💰 Cena systému: 6 250 € (vrátane inštalácie)
   Ročná úspora: ~494 €/rok
   Návratnosť: ~12.7 rokov
🌱 CO₂ úspora: 897 kg/rok
```

### 2. n8n Orchestračný workflow

Kompletný workflow (importovateľný JSON) prepájajúci Odoo, AI bota a Gmail:

```
Odoo nový lead
  → n8n zachytí webhook
  → spustí AI Bot konverzáciu
  → pošle zákazníkovi personalizovaný email s odkazom
  → po 30 min skontroluje výsledok konverzácie
  → aktualizuje Odoo (stage: Qualified + zozbierané dáta)
  → notifikuje obchodný tím
  → (ak nekvalifikovaný) follow-up email po 3 dňoch
```

Podmienka zadania — lead s kontaktom importovaný do Odoo — je plne splnená. Odoo je vstupný bod, zvyšok ide automaticky.

### 3. Embedovateľný Chat Widget

Vanilla JS widget bez externých závislostí, ktorý sa dá pridať na ecoprodukt.sk jedným riadkom kódu. Funguje na mobile aj desktope.

---

## Technická architektúra

```
[Zákazník] → [Chat Widget] → [AI Bot API / Railway]
                                    ↕
                             [Claude Haiku AI]
                             [PV Calculator]
                                    ↕
[Odoo CRM] ←→ [n8n Cloud] ←→ [AI Bot API]
                    ↓
              [Gmail → zákazník]
              [Gmail → obchodný tím]
```

**Náklady na prevádzku:** ~30–45 €/mesiac pri 500+ konverzáciách

---

## Prečo takýto prístup?

**Namiesto n8n/Make bota** som zvolil vlastný FastAPI backend z dôvodu:
- Flexibilita konverzačnej logiky (multi-turn, tool use, state management)
- Vlastný PV Calculator s reálnymi číslami pre SR
- Možnosť napojenia na Odoo XML-RPC API bez obmedzení no-code platformy
- Jednoduchý deployment a škálovanie

n8n rieši **orchestráciu** (kedy čo sa spustí), AI Bot rieši **inteligenciu** (čo povedať a vypočítať).

---

## Stav implementácie

| Komponent | Stav |
|-----------|------|
| AI Bot Backend (FastAPI + Claude) | ✅ Hotový |
| PV Calculator (kalkulácia systému, ROI) | ✅ Hotový |
| Chat Widget (HTML/CSS/JS) | ✅ Hotový |
| Odoo Webhook receiver | ✅ Hotový |
| n8n Workflow (10 nodes) | ✅ Hotový |
| Architecture Diagram | ✅ Hotový |
| Deployment na Railway | 🔄 Prebieha |

---

## Timeline do augusta 2026

| Fáza | Čas | Čo |
|------|-----|----|
| Fáza 1 | Hotová teraz | Funkčný prototyp, všetky komponenty |
| Fáza 2 | Jún 2026 | Prepojenie s reálnym Odoo ECO PRODUKT, testy s prvými leadmi |
| Fáza 3 | Júl 2026 | Doladenie dialógu podľa reálnych konverzácií, A/B testovanie |
| Fáza 4 | August 2026 | Produkčný launch, monitoring, optimalizácia |

---

## Čo ešte možno pridať (roadmapa)

- **WhatsApp/SMS notifikácie** cez Twilio (namiesto / okrem emailu)
- **PDF ponuka** generovaná automaticky po konverzácii
- **Kalkulačka dotácií** (Zelená domácnostiam II — aktuálne podmienky)
- **Booking systém** pre priamu rezerváciu obhliadky (Calendly/Cal.com integrácia)
- **Analýza konverzácií** — kde zákazníci odchádzajú, čo ich zaujíma
- **Viacjazyčná verzia** (CZ, HU) pre susedné trhy

---

*Celý zdrojový kód je dostupný na GitHub. Živý demo: https://ecoprodukt-bot.up.railway.app*
