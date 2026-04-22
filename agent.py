import anthropic
import sqlite3
import json
import os
import matplotlib
matplotlib.use("Agg")  # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from dotenv import load_dotenv
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
DB_PATH = "/home/b-elbikam/project/Nina_Bazar/db.sqlite3"
CHARTS_DIR = "/home/b-elbikam/project/Nina_Bazar/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are a Business Intelligence assistant for Nina_Bazar, 
a Moroccan e-commerce company. You have access to their live sales database.

Your capabilities:
- Query the SQLite database to answer business questions
- Generate charts and visualizations from data
- Provide actionable business insights in clear language

Guidelines:
- Always use get_schema first if you are unsure about table structure
- Prefer clear, concise answers with specific numbers
- When showing revenue, assume the currency is MAD (Moroccan Dirham)
- When a question benefits from a chart, generate one automatically
- Highlight anomalies or opportunities you notice in the data

You are being demonstrated to potential clients as a proof-of-concept 
Claude AI agent built by a freelance AI engineer."""

# ─────────────────────────────────────────────
# TOOLS DEFINITION
# ─────────────────────────────────────────────
tools = [
    {
        "name": "get_schema",
        "description": "Get the full database schema: all tables, columns, and types. Call this first when unsure about structure.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "query_database",
        "description": "Execute a read-only SQL SELECT query on the Nina_Bazar database and return results as JSON.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A valid SQLite SELECT query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "generate_chart",
        "description": "Generate a bar chart from labeled data and save it as a PNG file. Use for top products, revenue breakdowns, category comparisons, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Chart title"
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "X-axis labels (e.g. product names)"
                },
                "values": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Numeric values corresponding to each label"
                },
                "xlabel": {
                    "type": "string",
                    "description": "X-axis label"
                },
                "ylabel": {
                    "type": "string",
                    "description": "Y-axis label (e.g. 'Revenue (MAD)')"
                },
                "filename": {
                    "type": "string",
                    "description": "Output filename without extension (e.g. 'top_products_revenue')"
                }
            },
            "required": ["title", "labels", "values", "ylabel", "filename"]
        }
    }
]

# ─────────────────────────────────────────────
# TOOL EXECUTORS
# ─────────────────────────────────────────────
def tool_get_schema():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [
                {"name": row[1], "type": row[2], "notnull": bool(row[3]), "pk": bool(row[5])}
                for row in cursor.fetchall()
            ]
            schema[table] = columns

        conn.close()
        return json.dumps(schema, indent=2)
    except Exception as e:
        return f"Schema error: {str(e)}"


def tool_query_database(query):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "No results found."

        return json.dumps([dict(row) for row in rows], ensure_ascii=False, default=str)
    except Exception as e:
        return f"Database error: {str(e)}"


def tool_generate_chart(title, labels, values, ylabel, filename, xlabel=None):
    try:
        # Truncate long labels
        labels = [l[:22] + "…" if len(l) > 22 else l for l in labels]

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.Blues([0.4 + 0.6 * (i / max(len(values) - 1, 1)) for i in range(len(values))])
        bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=0.8)

        # Value labels on bars
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() * 1.01,
                f"{val:,.0f}",
                ha="center", va="bottom", fontsize=9, color="#333333"
            )

        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
        ax.set_ylabel(ylabel, fontsize=11)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=11)

        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="x", rotation=20, labelsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        plt.tight_layout()
        output_path = os.path.join(CHARTS_DIR, f"{filename}.png")
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        return f"Chart saved: {output_path}"
    except Exception as e:
        return f"Chart error: {str(e)}"


def execute_tool(name, inputs):
    print(f"  → [{name}]", end=" ")
    if name == "get_schema":
        print()
        return tool_get_schema()
    elif name == "query_database":
        print(inputs.get("query", "").split("\n")[0] + "...")
        return tool_query_database(inputs["query"])
    elif name == "generate_chart":
        print(inputs.get("title", ""))
        return tool_generate_chart(
            title=inputs["title"],
            labels=inputs["labels"],
            values=inputs["values"],
            ylabel=inputs["ylabel"],
            filename=inputs["filename"],
            xlabel=inputs.get("xlabel")
        )
    return "Unknown tool"


# ─────────────────────────────────────────────
# AGENT LOOP
# ─────────────────────────────────────────────
def run_agent(user_message, messages=None):
    if messages is None:
        messages = []

    messages.append({"role": "user", "content": user_message})

    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            answer = next(b.text for b in response.content if hasattr(b, "text"))
            messages.append({"role": "assistant", "content": answer})
            return answer, messages


# ─────────────────────────────────────────────
# INTERACTIVE SESSION
# ─────────────────────────────────────────────
def main():
    print("\n╔══════════════════════════════════════════╗")
    print("║    Nina_Bazar BI Agent  — Claude AI      ║")
    print("║    Type 'exit' to quit                   ║")
    print("╚══════════════════════════════════════════╝\n")

    messages = []  # persists across turns for multi-turn memory

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        print()
        answer, messages = run_agent(user_input, messages)
        print(f"\nAgent: {answer}\n")
        print("─" * 50)


if __name__ == "__main__":
    main()