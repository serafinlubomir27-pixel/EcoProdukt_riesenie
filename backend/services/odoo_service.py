"""
Odoo CRM integration service.
In production: uses Odoo JSON-RPC API.
In demo/dev: logs calls and returns mock responses.
"""
import os
import logging
from typing import Optional
from models.conversation import LeadData

logger = logging.getLogger(__name__)

ODOO_URL = os.environ.get("ODOO_URL", "")
ODOO_DB = os.environ.get("ODOO_DB", "")
ODOO_USER = os.environ.get("ODOO_USER", "")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "")
DEMO_MODE = not all([ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD])


async def update_lead_with_proposal(
    lead_id: int,
    lead_data: LeadData,
    proposal_text: str,
    conversation_id: str,
) -> bool:
    """Update Odoo CRM lead/opportunity with AI conversation results."""

    if DEMO_MODE:
        logger.info(
            f"[DEMO] Would update Odoo lead {lead_id}: "
            f"name={lead_data.name}, consumption={lead_data.annual_consumption_kwh} kWh, "
            f"region={lead_data.location_region}"
        )
        return True

    try:
        import xmlrpc.client

        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "crm.lead", "write",
            [[lead_id], {
                "description": f"AI Bot konverzácia ({conversation_id}):\n\n{proposal_text}",
                "stage_id": 2,  # "Qualified" stage — adjust to your pipeline
                "tag_ids": [(4, 1)],  # "AI Bot" tag
            }]
        )
        return True
    except Exception as e:
        logger.error(f"Odoo update failed for lead {lead_id}: {e}")
        return False


async def create_lead_from_bot(lead_data: LeadData, conversation_id: str) -> Optional[int]:
    """Create a new CRM lead in Odoo from bot conversation (fallback if webhook not used)."""

    if DEMO_MODE:
        logger.info(f"[DEMO] Would create Odoo lead: {lead_data.name} / {lead_data.email}")
        return 9999  # mock ID

    try:
        import xmlrpc.client

        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        lead_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "crm.lead", "create",
            [{
                "name": lead_data.name or "Nový lead z AI bota",
                "contact_name": lead_data.name,
                "email_from": lead_data.email,
                "phone": lead_data.phone,
                "description": f"Zdroj: AI Sales Bot\nKonverzácia: {conversation_id}\nSpotreba: {lead_data.annual_consumption_kwh} kWh\nKraj: {lead_data.location_region}",
                "tag_ids": [(4, 1)],
            }]
        )
        return lead_id
    except Exception as e:
        logger.error(f"Odoo create lead failed: {e}")
        return None
