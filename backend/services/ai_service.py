import anthropic
import json
import os
from typing import Optional
from models.conversation import Conversation, Message, MessageRole, ConversationState, LeadData
from services.pv_calculator import calculate_system, format_proposal_text
from data.pv_knowledge import SYSTEM_PROMPT

def _get_client():
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MODEL = "claude-haiku-4-5-20251001"

TOOLS = [
    {
        "name": "generate_proposal",
        "description": "Generuj návrh fotovoltického systému pre zákazníka keď máš dostatok informácií (spotreba, región, typ nehnuteľnosti). Zavolaj túto funkciu len raz keď máš kompletné dáta.",
        "input_schema": {
            "type": "object",
            "properties": {
                "annual_consumption_kwh": {
                    "type": "number",
                    "description": "Ročná spotreba elektriny v kWh"
                },
                "region": {
                    "type": "string",
                    "description": "Kraj na Slovensku (napr. 'bratislavský', 'košický')"
                },
                "roof_area_m2": {
                    "type": "number",
                    "description": "Plocha strechy v m² (voliteľné)"
                },
                "include_battery": {
                    "type": "boolean",
                    "description": "Zahrnúť batériový úložník do návrhu"
                },
                "lead_summary": {
                    "type": "object",
                    "description": "Zozbierané dáta o zákazníkovi",
                    "properties": {
                        "property_type": {"type": "string"},
                        "roof_orientation": {"type": "string"},
                        "budget_eur": {"type": "number"},
                        "timeline": {"type": "string"},
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"}
                    }
                }
            },
            "required": ["annual_consumption_kwh", "region"]
        }
    },
    {
        "name": "update_lead_data",
        "description": "Aktualizuj zozbierané dáta o zákazníkovi počas konverzácie. Volaj vždy keď zákazník poskytne novú informáciu.",
        "input_schema": {
            "type": "object",
            "properties": {
                "property_type": {"type": "string"},
                "annual_consumption_kwh": {"type": "number"},
                "roof_area_m2": {"type": "number"},
                "roof_orientation": {"type": "string"},
                "roof_shading": {"type": "string"},
                "location_region": {"type": "string"},
                "budget_eur": {"type": "number"},
                "timeline": {"type": "string"},
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"}
            }
        }
    }
]


def _messages_to_anthropic(conversation: Conversation) -> list:
    return [
        {"role": msg.role.value, "content": msg.content}
        for msg in conversation.messages
    ]


def process_tool_call(tool_name: str, tool_input: dict, conversation: Conversation) -> tuple[str, bool]:
    """Process a tool call and return (result_text, proposal_generated)."""

    if tool_name == "update_lead_data":
        for key, value in tool_input.items():
            if value is not None and hasattr(conversation.lead_data, key):
                setattr(conversation.lead_data, key, value)
        return "Lead data aktualizované.", False

    if tool_name == "generate_proposal":
        consumption = tool_input["annual_consumption_kwh"]
        region = tool_input.get("region", "default")
        roof_area = tool_input.get("roof_area_m2")
        include_battery = tool_input.get("include_battery", False)

        # Update lead data from proposal inputs
        lead_summary = tool_input.get("lead_summary", {})
        for key, value in lead_summary.items():
            if value is not None and hasattr(conversation.lead_data, key):
                setattr(conversation.lead_data, key, value)

        conversation.lead_data.annual_consumption_kwh = consumption
        conversation.lead_data.location_region = region

        proposal = calculate_system(
            annual_consumption_kwh=consumption,
            region=region,
            roof_area_m2=roof_area,
            include_battery=include_battery,
        )
        conversation.state = ConversationState.proposal
        return format_proposal_text(proposal), True

    return "Neznáma funkcia.", False


async def get_ai_response(conversation: Conversation, user_message: str) -> tuple[str, Conversation]:
    """Send message to Claude, handle tool calls, return assistant response."""

    conversation.messages.append(Message(role=MessageRole.user, content=user_message))

    messages = _messages_to_anthropic(conversation)
    proposal_generated = False

    # Agentic loop: Claude may call tools multiple times
    while True:
        response = _get_client().messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "tool_use":
            # Process all tool calls in this response
            tool_results = []
            assistant_content = response.content

            for block in response.content:
                if block.type == "tool_use":
                    result_text, is_proposal = process_tool_call(
                        block.name, block.input, conversation
                    )
                    if is_proposal:
                        proposal_generated = True
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    })

            # Add assistant response + tool results to messages
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})

        else:
            # Final text response
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text

            conversation.messages.append(
                Message(role=MessageRole.assistant, content=final_text)
            )
            return final_text, conversation


def get_welcome_message(lead_name: Optional[str] = None) -> str:
    name_part = f" {lead_name}" if lead_name else ""
    return (
        f"Dobrý deň{name_part}! Volám sa ECO asistent a som tu, aby som vám pomohol "
        f"navrhnúť fotovoltický systém na mieru — bez čakania na obchodníka.\n\n"
        f"Celý proces trvá asi 5 minút. Na základe vašich údajov vám okamžite vypočítam "
        f"optimálny systém, cenu a návratnosť investície.\n\n"
        f"Začneme jednoducho: **Aký typ nehnuteľnosti chcete vybaviť fotovoltaikou?**\n"
        f"_(Rodinný dom / Firma / Chata / Bytovka)_"
    )
