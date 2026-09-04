from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import CopilotConversation


@require_POST
def delete_conversation(request, conversation_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"message": "Please log in to use VirtualClinic AI."},
            status=401,
        )

    deleted, _ = CopilotConversation.objects.filter(
        pk=conversation_id,
        account=request.user.account,
    ).delete()

    if not deleted:
        return JsonResponse(
            {"message": "Conversation not found."},
            status=404,
        )

    return JsonResponse({"success": True})
