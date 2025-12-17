from graph.graph import app

if __name__ == "__main__":
    try:
        app.get_graph().draw_mermaid_png(output_file_path="graph.png")
    except Exception as e:
        print(f"An error occurred: {e}")
