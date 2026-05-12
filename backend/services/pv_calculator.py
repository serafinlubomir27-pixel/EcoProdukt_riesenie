from dataclasses import dataclass
from typing import Optional

# Solar irradiance by Slovak region (kWh/kWp/year)
IRRADIANCE_BY_REGION = {
    "bratislavský": 1100,
    "trnavský": 1080,
    "trenčínský": 1020,
    "nitrianský": 1090,
    "žilinský": 980,
    "banskobystrický": 1010,
    "prešovský": 970,
    "košický": 1050,
    "default": 1030,
}

ELECTRICITY_PRICE_EUR_KWH = 0.19  # avg Slovak household 2025
SYSTEM_PRICE_EUR_PER_KWP = 1250   # installed, incl. inverter, mounting, labor
BATTERY_PRICE_EUR_PER_KWH = 350
CO2_KG_PER_KWH = 0.172           # Slovak grid emission factor


@dataclass
class PVSystemProposal:
    system_kwp: float
    panel_count: int
    annual_production_kwh: float
    annual_savings_eur: float
    system_price_eur: float
    payback_years: float
    co2_saved_kg_year: float
    battery_kwh: Optional[float]
    battery_price_eur: Optional[float]
    total_price_eur: float
    self_consumption_pct: float
    region: str
    irradiance: int


def calculate_system(
    annual_consumption_kwh: float,
    region: str = "default",
    roof_area_m2: Optional[float] = None,
    include_battery: bool = False,
) -> PVSystemProposal:
    region_key = region.lower().replace(" kraj", "").strip()
    irradiance = IRRADIANCE_BY_REGION.get(region_key, IRRADIANCE_BY_REGION["default"])

    # Recommended system size covers ~70% of consumption
    recommended_kwp = round((annual_consumption_kwh * 0.70) / irradiance, 1)

    # Cap by roof area if provided (avg panel ~2 m², 400W each)
    if roof_area_m2:
        max_kwp_by_roof = round((roof_area_m2 * 0.7) * 0.4, 1)  # 70% usable, 400W/panel
        recommended_kwp = min(recommended_kwp, max_kwp_by_roof)

    # Round up to nearest 0.5 kWp
    recommended_kwp = round(round(recommended_kwp * 2) / 2, 1)
    recommended_kwp = max(3.0, recommended_kwp)  # minimum viable system

    panel_count = round(recommended_kwp / 0.4)
    annual_production = round(recommended_kwp * irradiance)

    # Self-consumption ratio (without battery ~40%, with battery ~70%)
    self_consumption_pct = 70 if include_battery else 40
    directly_used_kwh = min(annual_production * (self_consumption_pct / 100), annual_consumption_kwh)
    grid_export_kwh = annual_production - directly_used_kwh

    # Savings: directly used saves full price, exported earns feed-in (~0.06 €/kWh)
    annual_savings = round(directly_used_kwh * ELECTRICITY_PRICE_EUR_KWH + grid_export_kwh * 0.06, 0)

    system_price = round(recommended_kwp * SYSTEM_PRICE_EUR_PER_KWP, -2)  # round to nearest 100

    battery_kwh = None
    battery_price = None
    if include_battery:
        battery_kwh = round((annual_consumption_kwh / 365) * 1.5, 1)  # 1.5× daily consumption
        battery_kwh = min(battery_kwh, 15.0)  # max 15 kWh for residential
        battery_price = round(battery_kwh * BATTERY_PRICE_EUR_PER_KWH, -2)

    total_price = system_price + (battery_price or 0)
    payback_years = round(total_price / annual_savings, 1) if annual_savings > 0 else 99
    co2_saved = round(annual_production * CO2_KG_PER_KWH)

    return PVSystemProposal(
        system_kwp=recommended_kwp,
        panel_count=panel_count,
        annual_production_kwh=annual_production,
        annual_savings_eur=annual_savings,
        system_price_eur=system_price,
        payback_years=payback_years,
        co2_saved_kg_year=co2_saved,
        battery_kwh=battery_kwh,
        battery_price_eur=battery_price,
        total_price_eur=total_price,
        self_consumption_pct=self_consumption_pct,
        region=region,
        irradiance=irradiance,
    )


def format_proposal_text(p: PVSystemProposal) -> str:
    battery_line = ""
    if p.battery_kwh:
        battery_line = f"\n🔋 Batériový úložník: {p.battery_kwh} kWh — {p.battery_price_eur:,.0f} €"

    return f"""━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ VÁŠ NÁVRH FOTOVOLTIKY
━━━━━━━━━━━━━━━━━━━━━━━━━

🌞 Výkon systému: **{p.system_kwp} kWp** ({p.panel_count} panelov)
📍 Región: {p.region} ({p.irradiance} kWh/kWp/rok)
⚡ Ročná výroba: ~{p.annual_production_kwh:,} kWh{battery_line}

💰 FINANCIE
• Cena systému: **{p.system_price_eur:,.0f} €** (vrátane inštalácie)
• Ročná úspora: ~**{p.annual_savings_eur:,.0f} €/rok**
• Návratnosť investície: ~**{p.payback_years} rokov**
• Vlastná spotreba: {p.self_consumption_pct}%

🌱 Za rok ušetríte {p.co2_saved_kg_year} kg CO₂

━━━━━━━━━━━━━━━━━━━━━━━━━
Chcete si dohodnúť bezplatnú obhliadku a záväznú cenovú ponuku?"""
