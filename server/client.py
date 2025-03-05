import gradio as gr
from graph import part_1_graph, config
from langchain.schema import AIMessage, HumanMessage
from langchain_core.messages import ToolMessage

history_langchain_format = []

def predict(message, history):
    # Convert Gradio's 'history' into LangChain message objects
    for msg in history:
        if msg["role"] == "user":
            history_langchain_format.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history_langchain_format.append(AIMessage(content=msg["content"]))
            
    # Add the user's latest message
    history_langchain_format.append(HumanMessage(content=message))
    
    # Stream from the graph
    events = part_1_graph.stream({"messages": ("user", message)}, config, stream_mode="values")
    responses = []
    last_event = None
    for event in events:
        last_event = event  # keep reference to the last event received
        if "messages" in event:
            for m in event["messages"]:
                if isinstance(m, AIMessage):
                    responses.append(m.content)
    
    # Handle interrupt logic before calling tools
    snapshot = part_1_graph.get_state(config)
    tool_result = None
    while snapshot.next:
        try:
            user_input = input(
                "Do you approve of the above actions? Type 'y' to continue; otherwise, explain your requested changes.\n\n"
            )
        except Exception:
            user_input = "y"
    
        if user_input.strip() == "y":
            tool_result = part_1_graph.invoke(None, config)
        else:
            tool_result = part_1_graph.invoke(
                {
                    "messages": [
                        ToolMessage(
                            tool_call_id=last_event["messages"][-1].tool_calls[0]["id"],
                            content=f"API call denied by user. Reasoning: '{user_input}'. Continue assisting, accounting for the user's input.",
                        )
                    ]
                },
                config,
            )
        snapshot = part_1_graph.get_state(config)
    
    final_response = tool_result if tool_result is not None else (responses[-1] if responses else "No response")
    return {"text": final_response}

demo = gr.ChatInterface(
    fn=predict,
    type="messages"
)

demo.launch()