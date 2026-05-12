from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime
import uuid


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ConversationState(str, Enum):
    greeting = "greeting"
    qualifying = "qualifying"
    proposal = "proposal"
    closed = "closed"


class LeadData(BaseModel):
    property_type: Optional[str] = None
    annual_consumption_kwh: Optional[float] = None
    roof_area_m2: Optional[float] = None
    roof_orientation: Optional[str] = None
    roof_shading: Optional[str] = None
    location_region: Optional[str] = None
    budget_eur: Optional[float] = None
    timeline: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class Conversation(BaseModel):
    id: str = None
    messages: List[Message] = []
    state: ConversationState = ConversationState.greeting
    lead_data: LeadData = None
    created_at: datetime = None
    odoo_lead_id: Optional[int] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
        if self.lead_data is None:
            self.lead_data = LeadData()


class StartConversationRequest(BaseModel):
    lead_name: Optional[str] = None
    lead_email: Optional[str] = None
    lead_phone: Optional[str] = None
    odoo_lead_id: Optional[int] = None


class MessageRequest(BaseModel):
    content: str


class ConversationResponse(BaseModel):
    conversation_id: str
    message: str
    state: ConversationState
    lead_data: LeadData


class OdooLeadWebhook(BaseModel):
    lead_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
