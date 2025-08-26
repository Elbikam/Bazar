











def test_call_db_agent():
    """Test the tool to call the database agent."""
    question = "What is the total sales for the last month?"
    result = call_db_agent(question)
    assert result == "total sales for the last month: $1000"  # Example expected result