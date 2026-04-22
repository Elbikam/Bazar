from django.views.decorators.csrf import csrf_exempt
from dashboard.forms import LoginForm,Chat_form
from django.views.generic.base import TemplateView
from django.contrib.auth import authenticate,login,logout, user_logged_in
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import View
from ai_agent.interface import GeminiAPI,ServiceAgent
from dashboard.report import GetDataFromAI
from asgiref.sync import sync_to_async
import markdown
import logging
logger = logging.getLogger(__name__)
from dashboard.prompt import system_instruction,system_instruction_2
import json 
from django.utils.safestring import mark_safe
import re 
from django.contrib.auth.mixins import LoginRequiredMixin
from .service_storage import ServiceStorage
from django.http import JsonResponse
from ai_agent.agent import GeminiAPI
from django.views.decorators.csrf import csrf_protect
from ai_agent.agent import GeminiAPI
from asgiref.sync import async_to_sync
from google.genai.errors import ClientError
# ///////////////////////////////////////////////////////////////////////////////////////////////////////
logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = 'dashboard/dashboard.html'  


def login_user(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard:dashboard')  # Include the app namespace
            else:
                return render(request, 'dashboard/login.html', {'form': form})
    return render(request, 'dashboard/login.html', {'form': form})



def logout_user(request):
    logout(request)  # Log the user out
    return redirect('dashboard:login')  # 

class GenerateReport(View):
    """
    Async API view to generate AI-powered reports.
    Returns JSON with 'summary' and 'chart_data'.
    """
   
    async def get(self, request, *args, **kwargs):
        """
        1-Analyis sales for Dealer
        2-what is EOQ for each items,and provide chart
        3-i need to know which 20% items are responsable for 80% for sales,and provide Pareto chart
        4-How much did we buy this year 2026 for each item?,and provid chart"
        5-need to know which type of The are top saleing 200 g or 500 g,and provide chart?
        6-what are items that less sold it,and provid chart?
        7-write for me summary analysis for this week for my business,and also provid chart
        8-give me a new staretgy to increase sales or you have idea to help me 
        9-give me example of hypothesis testing in my business
            Marketing Campaign Effectiveness:
            Example: H0: The marketing campaign has no effect on sales.
            H1: The marketing campaign increases sales
        10-can you  offer a basic bar chart showing the number of items sold by each dealer     
        """
        query = "i need to know which 20% items are responsable for 80% for sales,and provide Pareto chart"
        full_query = f"{system_instruction}\n\nUser Query: {query}"


        try:
            # Initialize AI service
            service_agent = ServiceAgent()
            get_data_from_ai = GetDataFromAI(service_agent)

            # # # Call AI agent
            raw_ai_response = await  get_data_from_ai.call_agent(full_query)

            # 2. Extract the Artifact FIRST (Before Markdown conversion)
            artifact_pattern = re.compile(r'<artifact>(.*?)</artifact>', re.DOTALL)
            match = artifact_pattern.search(raw_ai_response)

            chart_html = ""
            text_only_response = raw_ai_response

            if match:
                # Save the HTML/JS code
                chart_html = match.group(1)
                
                # Remove the artifact from the main text string
                text_only_response = artifact_pattern.sub('',raw_ai_response)

            # 3. Convert the CLEANED text from Markdown to HTML
            # 'extensions' help with lists and newlines
            summary_html = markdown.markdown(text_only_response, extensions=['extra', 'nl2br'])

            context = { 
                'summary': mark_safe(summary_html),    # Rendered Markdown (Safe)
                'chart_artifact': mark_safe(chart_html) # Raw JS/HTML (Safe)
            }

            return await sync_to_async(render)(request, 'dashboard/ai_report.html',context)
        # except Exception as e:
        #     logger.error("Error generating report: %s", str(e), exc_info=True)
        #     return await sync_to_async(render)(request, 'dashboard/ai_report.html', {'error': str(e)})
        except ClientError as e:
            # --- SPECIFIC GOOGLE AI ERROR HANDLING ---
            logger.error(f"Google AI ClientError: {e}")
            
            error_message = "An error occurred with the AI service."
            
            if e.code == 429:
                error_message = "⚠️ System Busy: Rate limit exceeded. Please wait 60 seconds and refresh."
            elif e.code == 404:
                error_message = "⚠️ Configuration Error: The selected AI model was not found. Check interface.py."
            else:
                error_message = f"AI Service Error ({e.code}): {e.message}"

            return await sync_to_async(render)(request, 'dashboard/ai_report.html', {'error': error_message})

        except Exception as e:
            # --- GENERAL PYTHON ERROR HANDLING ---
            logger.error("Error generating report: %s", str(e), exc_info=True)
            return await sync_to_async(render)(request, 'dashboard/ai_report.html', {'error': f"Internal Server Error: {str(e)}"})





class ChatView(View):
    template_name = 'dashboard/chat.html'
    def get(self, request, *args, **kwargs):  
        return render(request,self.template_name)

class ControleConversation():
    def __init__(self):
        self.service_db = ServiceStorage()
        self.service_agent = ServiceAgent()


    def save_role_and_content(self,role,content):
        self.service_db.save_message(role,content)

    async def call_agent(self, content):
        return await self.service_agent.full_response_text(content)
      

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_text = data.get('message')
        full_query = f"{system_instruction}\n\nUser Query: {user_text}"
        if not user_text:
            return JsonResponse({'error': 'Empty message'}, status=400)

        conversation = ControleConversation()
        
        # 1. Save User Message
        conversation.save_role_and_content("user", user_text)

        # 2. Call AI Service
        # NOW: This will wait. 'ai_response' will be a STRING, not a Coroutine.
        ai_response = async_to_sync(conversation.call_agent)(full_query)

        # 3. Save AI Message
        # This will now work because ai_response is actual text
        conversation.save_role_and_content("AI", ai_response)

        # --- INTERFACE: Return JSON ---
        return JsonResponse({
            'status': 'success',
            'ai_response':ai_response, 
        })

    return JsonResponse({'error': 'Invalid method'}, status=405)
    

# ///////////////////////////////////////////////////////////////////////////////////////////////////////
import anthropic
import sqlite3
import json
import base64
import io
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

DB_PATH = "/home/b-elbikam/project/Nina_Bazar/db.sqlite3"
client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a Business Intelligence assistant for Nina_Bazar, 
a Moroccan e-commerce company. You have access to their live sales database.

Your capabilities:
- Query the SQLite database to answer any business question
- Generate charts and visualizations from data
- Provide actionable business insights and smart recommendations

Guidelines:
- Always use get_schema first if you are unsure about table structure
- Currency is MAD (Moroccan Dirham)
- When a question benefits from a chart, generate one automatically
- Be proactive: surface anomalies, trends, and opportunities even if not asked
- Keep answers concise but insightful — use tables and bullet points
- You are being shown to a potential client as a live AI BI agent demo"""

tools = [
    {
        "name": "get_schema",
        "description": "Get all tables and columns in the database. Call this first when unsure about structure.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "query_database",
        "description": "Execute a read-only SQL SELECT query and return results as JSON.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "A valid SQLite SELECT query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "generate_chart",
        "description": "Generate a bar chart from labeled data. Returns a base64 PNG image.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title":    {"type": "string"},
                "labels":   {"type": "array", "items": {"type": "string"}},
                "values":   {"type": "array", "items": {"type": "number"}},
                "ylabel":   {"type": "string"},
                "xlabel":   {"type": "string"},
                "filename": {"type": "string"}
            },
            "required": ["title", "labels", "values", "ylabel", "filename"]
        }
    }
]


# ── Tool executors ────────────────────────────────────────────────────────────

def tool_get_schema():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cursor.fetchall()]
        schema = {}
        for t in tables:
            cursor.execute(f"PRAGMA table_info({t})")
            schema[t] = [{"name": r[1], "type": r[2]} for r in cursor.fetchall()]
        conn.close()
        return json.dumps(schema, indent=2)
    except Exception as e:
        return f"Schema error: {e}"


def tool_query_database(query):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return json.dumps(rows, ensure_ascii=False, default=str) if rows else "No results."
    except Exception as e:
        return f"Database error: {e}"


def tool_generate_chart(title, labels, values, ylabel, filename, xlabel=None):
    try:
        labels = [l[:24] + "…" if len(l) > 24 else l for l in labels]
        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor("#0f1117")
        ax.set_facecolor("#0f1117")

        n = len(values)
        colors = ["#f5a623" if i == 0 else "#3d8bcd" for i in range(n)]
        bars = ax.bar(labels, values, color=colors, edgecolor="none", width=0.6)

        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() * 1.02,
                f"{val:,.0f}",
                ha="center", va="bottom", fontsize=9,
                color="#e0e0e0", fontweight="bold"
            )

        ax.set_title(title, fontsize=13, fontweight="bold", color="#ffffff", pad=14)
        ax.set_ylabel(ylabel, fontsize=10, color="#aaaaaa")
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=10, color="#aaaaaa")

        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.spines[:].set_visible(False)
        ax.tick_params(colors="#aaaaaa", labelsize=9)
        ax.xaxis.label.set_color("#aaaaaa")
        ax.yaxis.label.set_color("#aaaaaa")
        plt.xticks(rotation=20, ha="right", color="#aaaaaa")
        ax.grid(axis="y", color="#2a2d36", linewidth=0.8)

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        return json.dumps({"type": "chart", "data": b64, "title": title})
    except Exception as e:
        return f"Chart error: {e}"


def execute_tool(name, inputs):
    if name == "get_schema":
        return tool_get_schema()
    elif name == "query_database":
        return tool_query_database(inputs["query"])
    elif name == "generate_chart":
        return tool_generate_chart(
            title=inputs["title"], labels=inputs["labels"],
            values=inputs["values"], ylabel=inputs["ylabel"],
            filename=inputs["filename"], xlabel=inputs.get("xlabel")
        )
    return "Unknown tool"


# ── Agent loop ────────────────────────────────────────────────────────────────

def run_agent(user_message, history):
    messages = history + [{"role": "user", "content": user_message}]
    charts = []

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
                    # Collect charts separately
                    try:
                        parsed = json.loads(result)
                        if isinstance(parsed, dict) and parsed.get("type") == "chart":
                            charts.append({"data": parsed["data"], "title": parsed["title"]})
                    except Exception:
                        pass
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            answer = next(b.text for b in response.content if hasattr(b, "text"))
            messages.append({"role": "assistant", "content": answer})
            # Return updated history (without tool internals — only text turns)
            clean_history = [
                m for m in messages
                if isinstance(m.get("content"), str)
            ]
            return answer, charts, clean_history


# ── Django views ──────────────────────────────────────────────────────────────

def dashboard(request):
    return render(request, "dashboard/agent_dashboard.html")


@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body)
        user_message = body.get("message", "").strip()
        history = body.get("history", [])

        if not user_message:
            return JsonResponse({"error": "Empty message"}, status=400)

        answer, charts, new_history = run_agent(user_message, history)
        return JsonResponse({"answer": answer, "charts": charts, "history": new_history})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)