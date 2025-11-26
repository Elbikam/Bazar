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
        query ="What is top sales for this sales? to get data call db_agent and read carefully his instrcutions "

        try:
            # Initialize AI service
            gemini = GeminiAPI()
            service_agent = ServiceAgent(gemini)
            get_data_from_ai = GetDataFromAI(service_agent)

            # # Call AI agent
            raw_ai_response = await  get_data_from_ai.call_agent(query)
            html_response = markdown.markdown(raw_ai_response, extensions=['fenced_code', 'nl2br'])

            context = { 
                'report_data':html_response
            } 
           
            return await sync_to_async(render)(request, 'dashboard/ai_report.html',context)
        except Exception as e:
            logger.error("Error generating report: %s", str(e), exc_info=True)
            return await sync_to_async(render)(request, 'dashboard/ai_report.html', {'error': str(e)})

