
from langchain_core.tools import tool
from tools.schemas import ReservationResult, ReservationAgentResponse
from db.database import create_reservation, check_reservation_db, cancel_reservation_db

@tool
def table_reservation(first_name: str, last_name: str, year: int, month: int, day: int, time: str) -> ReservationAgentResponse:
    """
    Use this tool to create a reservation for a guest.
    You MUST collect ALL of the following before calling this tool:
    first name, last name, year, month, day, and time.
    Do NOT assume any field — ask for each one explicitly.
    Do NOT assume the year — always ask the guest for the year.
    Do NOT proceed with only a first name — always ask for the last name.
    If the guest gives a month name (e.g. "July"), convert it to an integer (7).
    If the guest gives a vague time (e.g. "evening"), ask for a specific time in HH:MM format.

    Args:
        first_name: First name of the guest — always ask explicitly, never assume
        last_name:  Last name of the guest — always ask explicitly, never assume
        year:       Year of the reservation, e.g. 2026 — always ask, never assume
        month:      Month as an integer, e.g. 7 for July
        day:        Day as an integer, e.g. 5
        time:       Time as a string in HH:MM format, e.g. "19:00"
    """
    reservation_id = create_reservation(first_name, last_name, year, month, day, time)
    return ReservationAgentResponse(
        answer=f"Reservation confirmed! Your booking reference is #{reservation_id}. See you on {day}/{month}/{year} at {time}, {first_name.title()}!",
        reservations=[ReservationResult(reservation_id=reservation_id, first_name=first_name,
                                        last_name=last_name, year=year, month=month,
                                        day=day, time=time, status="confirmed")]
    )

@tool
def check_reservation(first_name: str, last_name: str) -> ReservationAgentResponse:
    """
    Use this tool to check the status of an existing reservation for a guest.
    You MUST collect both first name AND last name before calling this tool.
    Do NOT assume or proceed with only one name — always ask for the last name explicitly.
    Do NOT assume the guest's last name from context or previous messages.

    Args:
        first_name: First name of the guest — always ask explicitly, never assume
        last_name:  Last name of the guest — always ask explicitly, never assume
    """
    results = check_reservation_db(first_name, last_name)
    if not results:
        return ReservationAgentResponse(
            answer=f"No reservation found for {first_name.title()} {last_name.title()}. Please double check the name.",
            reservations=[]
        )
    return ReservationAgentResponse(
        answer=f"Found {len(results)} reservation(s) for {first_name.title()} {last_name.title()}.",
        reservations=[ReservationResult(**r) for r in results]
    )

@tool
def cancel_reservation(first_name: str, last_name: str) -> ReservationAgentResponse:
    """
    Use this tool to cancel an existing reservation for a guest.
    You MUST collect both first name AND last name before calling this tool.
    Do NOT assume or proceed with only one name — always ask for the last name explicitly.
    Do NOT cancel without verbally confirming the full name with the guest first.
    Do NOT assume the cancellation is for the same person as a previous query in the conversation.

    Args:
        first_name: First name of the guest — always ask explicitly, never assume
        last_name:  Last name of the guest — always ask explicitly, never assume
    """
    result = cancel_reservation_db(first_name, last_name)
    if not result:
        return ReservationAgentResponse(
            answer=f"No active reservation found for {first_name.title()} {last_name.title()}. Please double check the name.",
            reservations=[]
        )
    return ReservationAgentResponse(
        answer=f"Reservation for {first_name.title()} {last_name.title()} on {result['day']}/{result['month']}/{result['year']} at {result['time']} has been successfully cancelled.",
        reservations=[ReservationResult(**result)]
    )
