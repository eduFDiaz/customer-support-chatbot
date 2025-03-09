from datetime import date, datetime
from typing import Annotated, Literal, Optional

from langchain_openai import ChatOpenAI

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage, AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate

from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.runnables import Runnable, RunnableLambda, RunnableConfig

from langchain_core.tools import tool

import uuid

from datetime import datetime
import parsedatetime as pdt # $ pip install parsedatetime

# Define state for dentist appointment booking
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages] # Required field for chatbot
    full_name: Optional[str] = None # Required field for booking appointments
    phone_number: Optional[str] = None # Required field for booking appointments
    appointment_purpose: Literal["checkup", "cleaning", "filling", "extraction", "routine"] # Required field for booking appointments
    appointment_date: Optional[datetime] = None # Required field for booking, listing, and rescheduling appointments
    reschedule_date: Optional[datetime] = None # Optional field for rescheduling appointments

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            user_id = configuration.get("user_id", None)
            state = {**state, "user_info": user_id}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
    
assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            '''You are a helpful customer support assistant for a dentist clinic.
            Customers will ask you to either book, list, reschedule, or cancel their dentist appointments.
            You should get the following information from them:
            - Full name
            - Phone number
            - Appointment purpose (checkup, cleaning, filling, extraction, routine)
            - Appointment date and time
            - Reschedule date (if applicable)
            If you are not able to discern this info, ask them to clarify! Do not attempt to wildly guess.

            Only after you are able to discern all the information, call the relevant tool.
            
            When the user greets you, introduce yourself and say all the things you can help with.

            Before calling any tool that will make a db write (i. e. book, reschedule or cancel), make sure to confirm with the user that want to go ahead with the action.
            Examples: 
            - "I will now book an appointment for you for date June 3rd at 2pm for a cleanup. Are you sure you want to proceed?".
            - "I will now cancel your appointment for June 3rd at 2pm for a cleanup. Are you sure you want to proceed?".
            - "I will now reschedule your appointment for June 3rd at 2pm for a cleanup to June 4th at 3pm. Are you sure you want to proceed?".

            Make sure you always call the parse_date tool before booking, rescheduling or cancelling an appointment, there should be no mistakes with the user provided date and time.
            \n\nCurrent user:\n<User>\n{user_info}\n</User>
            \nToday is: {today}.
            ''',
        ),
        ("placeholder", "{messages}"),
    ]
).partial(today=datetime.now)

question_category_prompt = '''You are a senior customer service specialist. 
Your task is to classify the incoming questions. 
Depending on your answer, question will be routed to the right team, so your task is crucial for our team. 
There are 4 possible question types: 
- BOOK - Book a dentist appointment
- LIST - list upcoming dentist appointments
- RESCHEDULE - Reschedule an existing dentist appointment
- CANCEL - Cancel an existing dentist appointment
Return in the output only one word (BOOK, LIST, RESCHEDULE or  CANCEL).
'''

@tool
def parse_date(
    date_string: str
) -> date:
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

# print(book_appointment.name)
# print(book_appointment.description)
# print(book_appointment.args)

@tool
def list_appointments(
    full_name: Optional[str] = None
    ) -> str:
    """Tool to list appointments

       Args:
            - full_name (str): Full name of the patient
            - phone_number (str): Phone number of the patient
            - appointment_purpose (str): Purpose of the appointment
            - appointment_date (date): Date of the appointment
       
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
    """Tool to reschedule an appointment

       Args:
            - full_name (str): Full name of the patient
            - phone_number (str): Phone number of the patient
            - appointment_purpose (str): Purpose of the appointment
            - appointment_date (date): Date of the appointment
       
       Returns:
            - str: A message confirming the appointment rescheduling or an error message
    """
    print(f"tool reschedule_appointment called with {full_name}")
    return f"Appointment rescheduled for {full_name} on {appointment_date} to {reschedule_date} for {appointment_purpose}."

@tool
def cancel_appointment(
    full_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    appointment_purpose: Optional[str] = None,
    appointment_date: Optional[datetime] = None
) -> str:
    """Tool to cancel an appointment

       Args:
            - full_name (str): Full name of the patient
            - phone_number (str): Phone number of the patient
            - appointment_purpose (str): Purpose of the appointment
            - appointment_date (date): Date of the appointment
       
       Returns:
            - str: A message confirming the appointment cancellation or an error message
    """
    print(f"tool cancel_appointment called with {full_name}")
    return f"Appointment cancelled for {full_name} on {appointment_date} for {appointment_purpose}."

@tool
def fetch_user_information(config: RunnableConfig) -> list[dict]:
    '''
    Tool to fetch user information from the database.
    '''
    configuration = config.get("configurable", {})
    user_id = configuration.get("user_id", None)
    user_info = [
        { "user_id": user_id,
          "full_name": "Eduardo Fernandez",
          "phone_number": "555-555-5555" 
        }
    ]
    # will implement the actual dynamodb database call here later on
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

# tavilyTool = TavilySearchResults(max_results=2)
safe_tools = [list_appointments, parse_date]
sensitive_tools = [book_appointment, reschedule_appointment, cancel_appointment]

sensitive_tools_names = [tool.name for tool in sensitive_tools]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
assistant_runnable = assistant_prompt | llm.bind_tools(
    safe_tools + sensitive_tools
)

def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)


def chatbot(state: State):
    message = assistant_runnable.invoke(state["messages"])
    # Because we will be interrupting during tool execution,
    # we disable parallel tool calling to avoid repeating any
    # tool invocations when we resume.
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

def user_info(state: State):
    return {"user_info": fetch_user_information.invoke({})}

def route_tools(state: State):
    next_node = tools_condition(state)
    # If no tools are invoked, return to the user
    if next_node == END:
        return END
    ai_message = state["messages"][-1]
    # This assumes single tool calls. To handle parallel tool calling, you'd want to
    # use an ANY condition
    first_tool_call = ai_message.tool_calls[0]
    if first_tool_call["name"] in sensitive_tools_names:
        return "sensitive_tools"
    return "safe_tools"

builder = StateGraph(State)

# Define nodes: these do the work
builder.add_node("fetch_user_info", user_info)
builder.add_edge(START, "fetch_user_info")
builder.add_node("assistant", Assistant(assistant_runnable))
builder.add_node("safe_tools", create_tool_node_with_fallback(safe_tools))
builder.add_node("sensitive_tools", create_tool_node_with_fallback(sensitive_tools))
builder.add_edge("fetch_user_info", "assistant")
builder.add_conditional_edges("assistant", route_tools, ["safe_tools", "sensitive_tools", END])
builder.add_edge("safe_tools", "assistant")
builder.add_edge("sensitive_tools", "assistant")

# The checkpointer lets the graph persist its state
# this is a complete memory for the entire graph.
memory = MemorySaver()
part_1_graph = builder.compile(
    checkpointer=memory,
    # interrupt_before=["sensitive_tools"],
    )

# this will come from the frontend or the user's session
thread_id = str(uuid.uuid4())

config = {
    "configurable": {
        # The user_id is used in our tools to
        # fetch the user's information from the Database
        "user_id": "3442 587242",
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}