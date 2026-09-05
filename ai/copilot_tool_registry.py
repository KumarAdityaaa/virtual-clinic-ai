from .copilot_tools import tool_get_my_appointments, tool_get_prescriptions
from .copilot_appointment_tools import tool_get_appointment, tool_prepare_reschedule, tool_confirm_reschedule, tool_prepare_cancel, tool_confirm_cancel


COPILOT_TOOL_DEFINITIONS = {
    "get_my_appointments": {
        "handler": tool_get_my_appointments,
        "roles": [
            "Patient",
            "Doctor",
        ],
        "description": "Get the current user's appointments.",
    },
    "get_prescriptions": {
        "handler": tool_get_prescriptions,
        "roles": [
            "Patient",
            "Doctor",
        ],
        "description": "Get the current user's prescriptions.",
    },
    "confirm_cancel": {
        "handler": tool_confirm_cancel,
        "roles": [
            "Patient",
            "Doctor",
            "Admin",
        ],
        "description": "Cancel an appointment after explicit user confirmation.",
    },
    "prepare_cancel": {
        "handler": tool_prepare_cancel,
        "roles": [
            "Patient",
            "Doctor",
            "Admin",
        ],
        "description": "Prepare an appointment cancellation. Does not cancel until explicitly confirmed.",
    },
    "confirm_reschedule": {
        "handler": tool_confirm_reschedule,
        "roles": [
            "Patient",
            "Doctor",
            "Admin",
        ],
        "description": "Apply a previously validated appointment reschedule after explicit user confirmation.",
    },
    "prepare_reschedule": {
        "handler": tool_prepare_reschedule,
        "roles": [
            "Patient",
            "Doctor",
            "Admin",
        ],
        "description": "Prepare a validated appointment reschedule. Does not save changes until confirmed.",
    },
    "get_appointment": {
        "handler": tool_get_appointment,
        "roles": [
            "Patient",
            "Doctor",
            "Admin",
        ],
        "description": "Get a specific appointment by ID when the user has permission to access it.",
    },
}






