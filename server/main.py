from graph_builder import build_graph, _print_event
from langchain_core.messages import ToolMessage

# Build the graph
part_1_graph, memory = build_graph()

# Create configuration for the graph
import uuid
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

def print_event(event):
    _printed = set()
    _print_event(event, _printed)

if __name__ == "__main__":
    # Let's create an example conversation a user might have with the assistant
    tutorial_questions = [
        "Hi there, I'd like to book and appointment for a checkup",
        "My name is Eduardo Fernandez.",
        "My phone number is 555-555-5555.",
        "I would like to book an appointment for Next Monday at 2PM.",
        "Yes please",
        "Can you please list all my future appointments?",
        "Sure, my name is Eduardo Fernandez and my phone number is 555-555-5555."
    ]

    _printed = set()
    # We can reuse the tutorial questions from part 1 to see how it does.
    for question in tutorial_questions:
        events = part_1_graph.stream(
            {"messages": ("user", question)}, config, stream_mode="values"
        )
        for event in events:
            _print_event(event, _printed)
        snapshot = part_1_graph.get_state(config)
        while snapshot.next:
            # We have an interrupt! The agent is trying to use a tool, and the user can approve or deny it
            # Note: This code is all outside of your graph. Typically, you would stream the output to a UI.
            # Then, you would have the frontend trigger a new run via an API call when the user has provided input.
            try:
                user_input = input(
                    "Do you approve of the above actions? Type 'y' to continue;"
                    " otherwise, explain your requested changed.\n\n"
                )
            except:
                user_input = "y"
            if user_input.strip() == "y":
                # Just continue
                result = part_1_graph.invoke(
                    None,
                    config,
                )
            else:
                # Satisfy the tool invocation by
                # providing instructions on the requested changes / change of mind
                result = part_1_graph.invoke(
                    {
                        "messages": [
                            ToolMessage(
                                tool_call_id=event["messages"][-1].tool_calls[0]["id"],
                                content=f"API call denied by user. Reasoning: '{user_input}'. Continue assisting, accounting for the user's input.",
                            )
                        ]
                    },
                    config,
                )
            snapshot = part_1_graph.get_state(config)

