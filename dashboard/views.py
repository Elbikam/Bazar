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
from dashboard.prompt import system_instruction
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
        4-How much did we buy this year for each item?,and provid chart"
        5-need to know which type of The are top saleing 200 g or 500 g,and provide chart?
        6-what are items that less sold it,and provid chart?
        7-write for me summary analysis for this week for my businis,and also provid chart
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

        if not user_text:
            return JsonResponse({'error': 'Empty message'}, status=400)

        conversation = ControleConversation()
        
        # 1. Save User Message
        conversation.save_role_and_content("user", user_text)

        # 2. Call AI Service
        # NOW: This will wait. 'ai_response' will be a STRING, not a Coroutine.
        ai_response = async_to_sync(conversation.call_agent)(user_text)

        # 3. Save AI Message
        # This will now work because ai_response is actual text
        conversation.save_role_and_content("AI", ai_response)

        # --- INTERFACE: Return JSON ---
        return JsonResponse({
            'status': 'success',
            'ai_response':ai_response, 
        })

    return JsonResponse({'error': 'Invalid method'}, status=405)