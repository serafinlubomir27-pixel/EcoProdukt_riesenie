# Email odpoveď — ECO PRODUKT zadanie

**Komu:** martina.kovacova@ecoprodukt.sk  
**Predmet:** Re: Zadanie — Junior špecialista AI automatizácia | Ľubomír Serafín

---

Dobrý deň, pani Kováčová,

ďakujem za zaslanie zadania. Namiesto prezentácie som rovno postavil funkčný systém — môžete ho ihneď vyskúšať:

🌐 **Live demo:** https://ecoproduktriesenie-production.up.railway.app
📁 **Zdrojový kód:** https://github.com/serafinlubomir27-pixel/EcoProdukt_riesenie

---

**Podmienka zo zadania (lead importovaný do Odoo) je splnená ako vstupný bod celého flow:**

```
Nový lead v Odoo
  → Odoo Automation Rule spustí webhook
  → n8n zachytí udalosť
  → spustí AI bota + pošle zákazníkovi personalizovaný email s odkazom na chat
  → zákazník chatuje s AI asistentom (bez obchodníka)
  → bot zbiera: typ nehnuteľnosti, spotreba, strecha, lokalita, budget
  → okamžite vygeneruje ponuku (kWp, cena, ROI, návratnosť)
  → n8n aktualizuje lead v Odoo (stage: Qualified + zozbierané dáta)
  → notifikácia obchodného tímu
```

Zvyšok architektúry (AI bot, kalkulácia, email flow, Odoo update) som navrhol a implementoval. V prílohe je kompletný **n8n workflow** (importovateľný JSON) a **interaktívny architecture diagram**.

**Čo som postavil:**
- FastAPI backend s Claude AI — 7-krokový kvalifikačný rozhovor
- PV Calculator — výpočet výkonu, ceny a ROI pre každý kraj SR
- Chat widget — embedovateľný na ecoprodukt.sk (jeden riadok kódu)
- n8n workflow — 12 nodes, Odoo → AI bot → email → Odoo update
- Prevádzka: ~30–45 €/mesiac pri stovkách konverzácií

---

**Forma spolupráce:** Živnosť (SZČO)

**Odmena:** 1 200 – 1 500 €/mesiac

---

S pozdravom,
**Ľubomír Serafín**
+421 911 445 903
lubomir.serafin@gmail.com

*Prílohy: ecoprodukt-sales-automation.json (n8n workflow), architecture.html (diagram)*
