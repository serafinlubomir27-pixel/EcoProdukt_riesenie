# Email odpoveď — ECO PRODUKT zadanie

**Komu:** Ing. Martina Kováčová, MBA (CMO, ECO PRODUKT)  
**Predmet:** Re: Junior špecialistu pre AI automatizáciu — vypracované zadanie

---

Dobrý deň, pani Kováčová,

ďakujem za zaslanie zadania — bol som rád, že sa nechce len "uvažovanie na papieri", ale reálne riešenie.

Namiesto prezentácie architektúry som preto **rovno postavil funkčný prototyp**, ktorý môžete ihneď vyskúšať:

🌐 **Live demo:** https://ecoprodukt-bot.up.railway.app  
📁 **Zdrojový kód:** https://github.com/[username]/ecoprodukt-ai-bot  
🏗️ **Architektúra (interaktívna):** https://ecoprodukt-bot.up.railway.app/static/docs/architecture.html

---

## Čo som postavil

Systém pozostáva z troch prepojených vrstiev:

**1. AI Sales Bot** — FastAPI backend s Claude AI, ktorý vedie zákazníka cez 7-krokový kvalifikačný rozhovor a okamžite vygeneruje personalizovanú ponuku (výkon systému, cena, ročná úspora, návratnosť). Bez čakania na obchodníka.

**2. n8n Workflow** (10 nodes, importovateľný JSON) — Odoo webhook → spustenie bota → personalizovaný email zákazníkovi → sledovanie výsledku → aktualizácia Odoo → notifikácia tímu. Podmienka zo zadania (lead importovaný do Odoo = vstupný bod) je plne splnená.

**3. Embedovateľný chat widget** — Vanilla JS, žiadne závislosti, dá sa pridať na ecoprodukt.sk jedným riadkom kódu.

Náklady na prevádzku: ~30–45 €/mesiac pri stovkách konverzácií.

---

## Odpovede na vaše otázky

**Forma spolupráce:** Uprednostňujem živnosť (SZČO) — pre obe strany najflexibilnejšia forma. Som flexibilný aj pri iných variantoch podľa vašich potrieb.

**Výška odmeny:** Očakávam 1 200 – 1 500 € mesačne (brutto/fakturácia), v závislosti od rozsahu a formy spolupráce. Sme otvorení diskusii.

---

Rád zodpoviem akékoľvek technické otázky alebo predvediem systém naživo pri online hovore.

S pozdravom,  
**Ľubomír Serafín**  
[telefón]  
[email]

---

*Prílohy: architecture.html (architektúra systému), ecoprodukt-sales-automation.json (n8n workflow)*
