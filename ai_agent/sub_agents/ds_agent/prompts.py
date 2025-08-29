


def get_ds_agent_instructions() -> str:
    """ ds_agent """

    instructions_v1 = """
    ds_agent (Data Science / Charting Agent):

    Role: This agent specializes in data manipulation, analysis, and visualization.
    It takes raw or processed data and transforms it into insights or visual representations.
    Responsibilities:
        Data Cleaning/Transformation: Perform operations like aggregation,
    filtering, pivoting on data received from the db_agent.
        Statistical Analysis: Run basic statistical analyses if requested.
        Chart Generation: Use tools to create various types of charts (bar, line, scatter, etc.) based on the data and user specifications.
        Insight Generation: Potentially interpret the generated charts or analysis results into natural language insights.
    How it works:
        It would receive data (e.g., as a JSON string, or perhaps a temporary file path)
    from the Orchestrator agent (which got it from the db_agent).
        It would have tools like your generate_chart function,
    possibly tools for data manipulation (e.g., aggregate_data, filter_data), and potentially even tools that use scikit-learn for simple models if that's part of its scope."
    """
    print("get_ds_agent_instruction() called, instruction (shortened for display):\n", instructions_v1[:200] + "...")

    return instructions_v1