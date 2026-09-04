from .copilot_tool_registry import COPILOT_TOOL_DEFINITIONS


def get_available_copilot_tools(request):
    role = request.user.account

    from .copilot import get_user_role

    role_name = get_user_role(role)

    available = {}

    for name, definition in COPILOT_TOOL_DEFINITIONS.items():
        if role_name in definition["roles"]:
            available[name] = {
                "description": definition["description"],
            }

    return available
