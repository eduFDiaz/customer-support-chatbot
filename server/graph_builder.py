from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from state import State
from tools import fetch_user_information, handle_tool_error
from assistant import create_assistant

def build_graph():
    assistant, assistant_runnable, safe_tools, sensitive_tools = create_assistant()
    sensitive_tools_names = [tool.name for tool in sensitive_tools]

    def user_info(state: State):
        return {"user_info": fetch_user_information({})}

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

    def create_tool_node_with_fallback(tools: list) -> dict:
        return ToolNode(tools).with_fallbacks(
            [RunnableLambda(handle_tool_error)], exception_key="error"
        )

    builder = StateGraph(State)

    # Define nodes: these do the work
    builder.add_node("fetch_user_info", user_info)
    builder.add_edge(START, "fetch_user_info")
    builder.add_node("assistant", assistant)
    builder.add_node("safe_tools", create_tool_node_with_fallback(safe_tools))
    builder.add_node("sensitive_tools", create_tool_node_with_fallback(sensitive_tools))
    builder.add_edge("fetch_user_info", "assistant")
    builder.add_conditional_edges("assistant", route_tools, ["safe_tools", "sensitive_tools", END])
    builder.add_edge("safe_tools", "assistant")
    builder.add_edge("sensitive_tools", "assistant")

    # The checkpointer lets the graph persist its state
    memory = MemorySaver()
    graph = builder.compile(
        checkpointer=memory,
        # interrupt_before=["sensitive_tools"],
    )

    return graph, memory

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
