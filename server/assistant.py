from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI
from state import State
from tools import parse_date, book_appointment, list_appointments, reschedule_appointment, cancel_appointment
from prompts import assistant_prompt

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

def create_assistant():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    safe_tools = [list_appointments, parse_date]
    sensitive_tools = [book_appointment, reschedule_appointment, cancel_appointment]
    
    assistant_runnable = assistant_prompt | llm.bind_tools(
        safe_tools + sensitive_tools
    )
    
    return Assistant(assistant_runnable), assistant_runnable, safe_tools, sensitive_tools
