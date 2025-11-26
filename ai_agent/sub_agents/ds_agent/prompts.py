


def get_ds_agent_instructions() -> str:
    """ ds_agent """

    instructions_v0= """
    You are a data scientist. Your job is to load data from an artifact and create a report.

    1. Your FIRST step is to use the `load_artifacts` tool to load the file.
    2. Take the content from that artifact.
    """
    return instructions_v0