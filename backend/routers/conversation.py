from fastapi import APIRouter, HTTPException
from models.conversation import (
    Conversation, StartConversationRequest, MessageRequest,
    ConversationResponse, Message, MessageRole
)
from services.ai_service import get_ai_response, get_welcome_message
from services.odoo_service import create_lead_from_bot

router = APIRouter(tags=["conversation"])

# In-memory store (use Redis in production)
conversations: dict[str, Conversation] = {}


@router.post("/conversation/start", response_model=ConversationResponse)
async def start_conversation(req: StartConversationRequest):
    conv = Conversation()

    if req.lead_name:
        conv.lead_data.name = req.lead_name
    if req.lead_email:
        conv.lead_data.email = req.lead_email
    if req.lead_phone:
        conv.lead_data.phone = req.lead_phone
    if req.odoo_lead_id:
        conv.odoo_lead_id = req.odoo_lead_id

    welcome = get_welcome_message(req.lead_name)
    conv.messages.append(Message(role=MessageRole.assistant, content=welcome))
    conversations[conv.id] = conv

    return ConversationResponse(
        conversation_id=conv.id,
        message=welcome,
        state=conv.state,
        lead_data=conv.lead_data,
    )


@router.post("/conversation/{conversation_id}/message", response_model=ConversationResponse)
async def send_message(conversation_id: str, req: MessageRequest):
    conv = conversations.get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Konverzácia nenájdená")

    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Správa nemôže byť prázdna")

    response_text, updated_conv = await get_ai_response(conv, req.content)
    conversations[conversation_id] = updated_conv

    # Auto-create Odoo lead when we have contact info (if not from Odoo webhook)
    if (
        updated_conv.lead_data.email
        and not updated_conv.odoo_lead_id
        and updated_conv.state.value == "proposal"
    ):
        lead_id = await create_lead_from_bot(updated_conv.lead_data, conversation_id)
        if lead_id:
            updated_conv.odoo_lead_id = lead_id

    return ConversationResponse(
        conversation_id=conversation_id,
        message=response_text,
        state=updated_conv.state,
        lead_data=updated_conv.lead_data,
    )


@router.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    conv = conversations.get(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Konverzácia nenájdená")

    last_message = conv.messages[-1].content if conv.messages else ""
    return ConversationResponse(
        conversation_id=conversation_id,
        message=last_message,
        state=conv.state,
        lead_data=conv.lead_data,
    )
