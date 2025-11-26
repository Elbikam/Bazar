from dashboard.forms import LoginForm
from django.views.generic.base import TemplateView
from django.contrib.auth import authenticate,login,logout
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
from dashboard.test_dashboard.fake_ai_response import fake_ai_response
from django.utils.safestring import mark_safe
import markdown 
import re 
# ///////////////////////////////////////////////////////////////////////////////////////////////////////
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
        query = "i need to know distruction of sales  ,and provide chart."
        full_query = f"{system_instruction}\n\nUser Query: {query}"


        try:
            # Initialize AI service
            gemini = GeminiAPI()
            service_agent = ServiceAgent(gemini)
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
        except Exception as e:
            logger.error("Error generating report: %s", str(e), exc_info=True)
            return await sync_to_async(render)(request, 'dashboard/ai_report.html', {'error': str(e)})

