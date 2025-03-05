from graph import part_1_graph

try:
    from IPython.display import Image, display
    image = Image(part_1_graph.get_graph().draw_mermaid_png())
    # save the graph as an image
    with open("graph.png", "wb") as file:
        file.write(image.data)

except Exception:
    # This requires some extra dependencies and is optional
    pass