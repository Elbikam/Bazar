import os
import json
import anthropic
from dotenv import load_dotenv


load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


import anthropic
import sqlite3
import json

client = anthropic.Anthropic()
DB_PATH = "/home/b-elbikam/project/Nina_Bazar/db.sqlite3"

tools = [
    {
        "name": "query_database",
        "description": "Run a read-only SQL query on the Nina_Bazar SQLite database",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL SELECT query to execute"}
            },
            "required": ["query"]
        }
    }
]

def execute_tool(name, inputs):
    if name == "query_database":
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row  # returns dict-like rows
            cursor = conn.cursor()
            cursor.execute(inputs["query"])
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return "No results found."
            
            # Convert to list of dicts for Claude to read
            result = [dict(row) for row in rows]
            return json.dumps(result, ensure_ascii=False)
        
        except Exception as e:
            return f"Database error: {str(e)}"

def run_agent(user_message):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  → Tool called: {block.name}")
                    print(f"  → Query: {block.input.get('query')}")
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "user", "content": tool_results})
        
        elif response.stop_reason == "end_turn":
            return next(b.text for b in response.content if hasattr(b, 'text'))

print(run_agent("What are the top 5 products by revenue?"))