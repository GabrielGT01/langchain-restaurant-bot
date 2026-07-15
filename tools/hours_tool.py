
from typing import Optional
from langchain_core.tools import tool
from tools.schemas import OpeningHoursResult, OpeningHoursResponse
from db.database import get_details_opening_time_all

@tool
def opening_hours_tool(day: Optional[str] = None) -> OpeningHoursResponse:
    """
    Use this tool to answer customer inquiries about restaurant opening hours,
    closing times, and any special notes such as kitchen closing early,
    breakfast, or brunch availability.

    Args:
        day: Optional. One of "Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday".
             If omitted, returns hours for the full week.

    Returns an OpeningHoursResponse with:
      - answer: plain-English summary
      - hours:  list of day(s) with opening time, closing time, and note
    """
    all_hours = get_details_opening_time_all()
    if day:
        day = day.capitalize()
        match = [r for r in all_hours if r["day"] == day]
        if not match:
            return OpeningHoursResponse(answer=f"No opening hours found for {day}.", hours=[])
        info = match[0]
        return OpeningHoursResponse(
            answer=f"On {day}, we're open from {info['opens']} to {info['closes']}.",
            hours=[OpeningHoursResult(day=info["day"], opens=info["opens"], closes=info["closes"], note=info["note"])]
        )
    return OpeningHoursResponse(
        answer="Here are our opening hours for the week.",
        hours=[OpeningHoursResult(day=r["day"], opens=r["opens"], closes=r["closes"], note=r["note"]) for r in all_hours]
    )
