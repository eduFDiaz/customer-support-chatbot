from datetime import datetime
from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# Define state for dentist appointment booking
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages] # Required field for chatbot
    full_name: Optional[str] = None # Required field for booking appointments
    phone_number: Optional[str] = None # Required field for booking appointments
    appointment_purpose: Literal["checkup", "cleaning", "filling", "extraction", "routine"] # Required field for booking appointments
    appointment_date: Optional[datetime] = None # Required field for booking, listing, and rescheduling appointments
    reschedule_date: Optional[datetime] = None # Optional field for rescheduling appointments
