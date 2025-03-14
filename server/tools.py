import parsedatetime as pdt
from datetime import datetime
from typing import Optional
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage

@tool
def parse_date(
    date_string: str
) -> datetime:
    '''
    Tool to parse a date and time when a date/time in natural language is provided by the user.
    '''
    cal = pdt.Calendar()
    now = datetime.now()
    print(f"tool parse_date called with {date_string}")
    return cal.parseDT(date_string, now)[0]

@tool
def book_appointment(
    full_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    appointment_purpose: Optional[str] = None,
    appointment_date: Optional[datetime] = None
    ) -> str:
    """Tool to book and appointment
       
       Args:
            - full_name (str): Full name of the patient
            - phone_number (str): Phone number of the patient
            - appointment_purpose (str): Purpose of the appointment
            - appointment_date (date): Date of the appointment

       Returns:
            - str: A message confirming the appointment booking or an error message
    """
    print(f"Appointment booked for {full_name} on {appointment_date} for {appointment_purpose}.")
    return f"Appointment booked for {full_name} on {appointment_date} for {appointment_purpose}."

@tool
def list_appointments(
    full_name: Optional[str] = None
    ) -> str:
    """Tool to list appointments

       Args:
            - full_name (str): Full name of the patient
       
       Returns:
            - str: A message listing all the appointments for the patient
    """
    print(f"tool list_appointments called with {full_name}")
    return { "appointments" : [
        "Appointment booked for Eduardo Fernandez on 2025-03-03 14:00:00 for checkup",
        "Appointment booked for Eduardo Fernandez on 2025-06-03 15:30:00 for cleaning"
        ]}

@tool
def reschedule_appointment(
    full_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    appointment_purpose: Optional[str] = None,
    appointment_date: Optional[datetime] = None,
    reschedule_date: Optional[datetime] = None) -> str:
    """Tool to reschedule an appointment"""
    print(f"tool reschedule_appointment called with {full_name}")
    return f"Appointment rescheduled for {full_name} on {appointment_date} to {reschedule_date} for {appointment_purpose}."

@tool
def cancel_appointment(
    full_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    appointment_purpose: Optional[str] = None,
    appointment_date: Optional[datetime] = None
) -> str:
    """Tool to cancel an appointment"""
    print(f"tool cancel_appointment called with {full_name}")
    return f"Appointment cancelled for {full_name} on {appointment_date} for {appointment_purpose}."

@tool
def fetch_user_information(config: RunnableConfig = None) -> list[dict]:
    '''
    Tool to fetch user information from the database.
    '''
    user_id = "default_user"
    if config and isinstance(config, dict):
        configuration = config.get("configurable", {})
        user_id = configuration.get("user_id", user_id)

    user_info = [
        { "user_id": user_id,
          "full_name": "Eduardo Fernandez",
          "phone_number": "555-555-5555" 
        }
    ]
    return user_info

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }
