import json
from datetime import datetime
import os

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from google import genai

from .models import CopilotConversation, CopilotMessage
from .copilot_tool_access import get_available_copilot_tools
from .copilot_tool_registry import COPILOT_TOOL_DEFINITIONS
from .copilot import (
    get_copilot_context,
    get_my_appointments,
)


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


@require_POST
def copilot(request):

    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "message":
                    "Please log in to use VirtualClinic AI."
            },
            status=401,
        )

    user_message = request.POST.get(
        "message",
        ""
    ).strip()

    conversation_id = request.POST.get(
        "conversation_id"
    )

    if not user_message:
        return JsonResponse(
            {
                "message":
                    "Please enter a message."
            },
            status=400,
        )

    conversation = None

    if conversation_id:
        try:
            conversation = CopilotConversation.objects.get(
                pk=conversation_id,
                account=request.user.account,
            )
        except CopilotConversation.DoesNotExist:
            return JsonResponse(
                {
                    "message":
                        "That conversation could not be found."
                },
                status=404,
            )

    if conversation is None:
        conversation = CopilotConversation.objects.create(
            account=request.user.account,
            title=user_message[:60] or "New Chat",
        )

    CopilotMessage.objects.create(
        conversation=conversation,
        role="user",
        content=user_message,
    )

    context = get_copilot_context(request)
    today = timezone.localdate().isoformat()

    appointments = get_my_appointments(request)
    available_tools = get_available_copilot_tools(request)

    previous_messages = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in conversation.messages.order_by("created")
        if message.pk != conversation.messages.order_by("-created").first().pk
    ]

    prompt = f"""
You are VirtualClinic AI Copilot.

USER:
{context["name"]}

TODAY'S DATE:
{today}

ROLE:
{context["role"]}

CONVERSATION HISTORY:
{json.dumps(previous_messages, indent=2)}

USER MESSAGE:
{user_message}

AVAILABLE AI TOOLS:
{json.dumps(available_tools, indent=2)}

USER APPOINTMENTS:
{json.dumps(appointments, indent=2)}

Return a JSON object with exactly these fields:

message:
A short natural-language response.

links:
An array of objects containing:
- label
- url

action:
Either null or an object containing:
- tool
- arguments

Only use a tool that appears in AVAILABLE AI TOOLS.
Do not execute actions yourself.
For read-only questions, use the appropriate available tool.

When the user refers to a specific appointment:
- Use get_appointment with the appointment ID when that ID is available.
- Never invent an appointment ID.
- Respect the user's role and permissions.

When the user asks to reschedule an appointment:
- Use prepare_reschedule.
- Provide the appointment ID.
- Provide new_start in ISO 8601 format.
- If the user gives only a new start time, preserve the existing appointment duration.
- Never invent a new date or time.

When the user asks to cancel an appointment:
- Use prepare_cancel.
- Provide the appointment ID.
- Never cancel an appointment without explicit confirmation.



For appointment-related questions:
- Include one link for every relevant appointment.
- Use the exact appointment URL provided in the appointment data.
- Do not invent URLs.

For non-appointment questions:
- links may be an empty array.

Rules:
- Use only the supplied appointment data.
- Do not invent appointments.
- Do not expose data belonging to other users.
- Do not diagnose medical conditions.
- Do not prescribe medicines.
- Do not modify database records.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        },
    )

    try:
        result = json.loads(response.text)

    except (json.JSONDecodeError, TypeError):
        result = {
            "message": response.text,
            "links": [],
        }

    action = result.get("action")

    if action and action.get("tool"):
        tool_name = action.get("tool")
        tool_definition = COPILOT_TOOL_DEFINITIONS.get(tool_name)

        if tool_definition and tool_name in available_tools:
            tool_arguments = action.get("arguments", {}) or {}
            tool_result = tool_definition["handler"](
                request,
                **tool_arguments
            )

            result["tool_result"] = tool_result

            if tool_name in ["prepare_reschedule", "prepare_cancel"] and tool_result.get("requires_confirmation"):
                result["confirmation"] = tool_result["data"]
                result["confirmation"]["action"] = tool_name

            if tool_name == "get_appointment" and tool_result.get("success"):
                appointment = tool_result["data"]

                start_time = datetime.fromisoformat(
                    appointment["start_time"]
                )
                end_time = datetime.fromisoformat(
                    appointment["end_time"]
                )

                readable_date = start_time.strftime("%B %d, %Y").replace(
                    " 0", " "
                )

                readable_start = start_time.strftime(
                    "%I:%M %p"
                ).lstrip("0")

                readable_end = end_time.strftime(
                    "%I:%M %p"
                ).lstrip("0")

                result["message"] = (
                    f"Appointment #{appointment['id']} with "
                    f"{appointment['doctor']} for "
                    f"{appointment['patient']}.\n\n"
                    f"{readable_date} · "
                    f"{readable_start} – {readable_end}\n"
                    f"Status: {appointment['status']} · "
                    f"Type: {appointment['type']}\n"
                    f"{appointment['symptom']} · "
                    f"{appointment['hospital']}"
                )

                result["links"] = [
                    {
                        "label": (
                            f"Open appointment #{appointment['id']}"
                        ),
                        "url": (
                            f"/appointment/update/?pk={appointment['id']}"
                        ),
                    }
                ]

            elif tool_result.get("success") is False:
                result["message"] = tool_result.get(
                    "error",
                    "I could not retrieve that appointment."
                )

    CopilotMessage.objects.create(
        conversation=conversation,
        role="assistant",
        content=result.get(
            "message",
            ""
        ),
    )

    conversation.save(
        update_fields=["updated"]
    )

    return JsonResponse(
        {
            "message": result.get(
                "message",
                ""
            ),
            "links": result.get(
                "links",
                []
            ),
            "confirmation": result.get("confirmation"),
            "conversation_id": conversation.pk,
            "context": context,
        }
    )




























