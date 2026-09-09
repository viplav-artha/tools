from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from tools.registry import tool


@tool(
    name="get_current_time",
    description=(
        "Get the current date and time in a given IANA timezone (e.g. "
        "'America/New_York', 'Asia/Kolkata'). Defaults to UTC if no "
        "timezone is given. Use this whenever you need to know today's "
        "date or the current time — you do not otherwise know it."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": (
                    "An IANA timezone name, e.g. 'America/New_York' or "
                    "'Asia/Kolkata'. Defaults to 'UTC' if omitted."
                ),
            }
        },
        "required": [],
    },
)
async def get_current_time(timezone: str = "UTC") -> str:
    try:
        zone = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        raise ValueError(
            f"Unknown timezone: {timezone!r}. Use a valid IANA timezone "
            "name, e.g. 'America/New_York' or 'Asia/Kolkata'."
        )

    now = datetime.now(zone)
    return now.strftime("%Y-%m-%d %H:%M:%S %Z (%z)")
