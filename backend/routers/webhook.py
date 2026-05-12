from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.conversation import (
    Conversation, OdooLeadWebhook, Message, MessageRole
)
from services.ai_service import get_welcome_message
import logging

router = APIRouter(tags=["webhook"])
logger = logging.getLogger(__name__)

# Shared store reference (imported by main.py)
from routers.conversation import conversations


@router.post("/odoo/new-lead", status_code=200)
async def odoo_new_lead(payload: OdooLeadWebhook, background_tasks: BackgroundTasks):
    """
    Webhook called by Odoo (via n8n) when a new lead/contact is created.
    Creates a conversation pre-loaded with lead data, ready for the AI bot to start.
    Returns conversation_id which n8n uses to send the first message via email/WhatsApp.
    """
    conv = Conversation()
    conv.odoo_lead_id = payload.lead_id
    conv.lead_data.name = payload.name
    conv.lead_data.email = payload.email
    conv.lead_data.phone = payload.phone

    welcome = get_welcome_message(payload.name)
    conv.messages.append(Message(role=MessageRole.assistant, content=welcome))
    conversations[conv.id] = conv

    logger.info(f"New Odoo lead #{payload.lead_id} → conversation {conv.id} created")

    return {
        "status": "ok",
        "conversation_id": conv.id,
        "lead_id": payload.lead_id,
        "first_message": welcome,
        "chat_url": f"/chat?conversation_id={conv.id}",
    }


@router.get("/odoo/health")
async def webhook_health():
    return {"status": "ok", "active_conversations": len(conversations)}
