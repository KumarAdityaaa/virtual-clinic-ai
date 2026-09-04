from django.http import JsonResponse
from .models import CopilotConversation


def conversations(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"message": "Please log in to use VirtualClinic AI."},
            status=401,
        )

    conversations = (
        CopilotConversation.objects
        .filter(account=request.user.account, messages__isnull=False)
        .distinct()
        .prefetch_related("messages")
    )

    result = []

    for conversation in conversations:
        messages = list(conversation.messages.all())

        if not messages:
            continue

        title = conversation.title

        if title == "New Chat":
            title = messages[0].content[:60]

        result.append(
            {
                "id": conversation.pk,
                "title": title,
                "created": conversation.created,
                "updated": conversation.updated,
                "messages": [
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                    for message in messages
                ],
            }
        )

    return JsonResponse({"conversations": result})


def new_conversation(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"message": "Please log in to use VirtualClinic AI."},
            status=401,
        )

    conversation = CopilotConversation.objects.create(
        account=request.user.account,
        title="New Chat",
    )

    return JsonResponse(
        {
            "conversation": {
                "id": conversation.pk,
                "title": conversation.title,
            }
        }
    )
