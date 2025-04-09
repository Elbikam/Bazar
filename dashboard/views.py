from django.utils import timezone
from django.views.generic import TemplateView
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect
from django.contrib import messages
from dashboard.forms import  LoginForm
import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
import requests
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from stock.models import Stock, StockAlert
from sale.models import Sale, Order_Line, Refund, Refund_Line, Dealer, SaleToDealer
from django.utils import timezone
from datetime import timedelta
import pandas as pd
import plotly.express as px
import os
import google.generativeai as genai
from . import reporting 
from .reporting import *
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.ai.generativelanguage as glm # For FunctionResponse
from datetime import datetime # Needed for date parsing
import plotly.graph_objects as go
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


# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

@csrf_exempt
def ai_report_generator(request):
    """Handles user prompts and interacts with the Gemini API using a loop for function calls."""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        # Define the tools the AI can use
        tools = [
            glm.Tool(
                function_declarations=[
                    glm.FunctionDeclaration(
                        name="get_sales_data",
                        description="Retrieves detailed sales data (line items) for a specific month and year. Defaults to the current month if date is not provided.",
                        parameters=glm.Schema(
                            type=glm.Type.OBJECT,
                            properties={
                                'date': glm.Schema(type=glm.Type.STRING, description="Optional. The date (YYYY-MM) for which to retrieve sales data. E.g., '2023-10'.")
                            },
                            required=[]
                        )
                    ),
                    glm.FunctionDeclaration(
                        name="get_refunds_data",
                        description="Retrieves detailed refund data (line items) for a specific month and year. Defaults to the current month if date is not provided.",
                        parameters=glm.Schema(
                            type=glm.Type.OBJECT,
                            properties={
                                'date': glm.Schema(type=glm.Type.STRING, description="Optional. The date (YYYY-MM) for which to retrieve refund data. E.g., '2023-10'.")
                            },
                            required=[]
                        )
                    )
                ]
            )
        ]

        # Updated Initial prompt instructing the AI
        initial_prompt = """### AI Agent Responsibilities
         AI Agent Responsibilities
    Based *only* on the information provided by the available tools (get_sales_data, get_refunds_data),
      generate a comprehensive report that includes:
      1. **Sales Data Overview**: Total sales amount, number of transactions, and sales .
      2. **Refund Data Overview**: Total refund amount, number of refunds.
      3. **Visualizations**: Describe 1-2 effective visualizations for the combined data
        (e.g., bar chart for sales/refunds by item, line chart for totals if multiple periods were requested).
      4. **Insights and Recommendations**: Provide 2-3 concise insights and actionable recommendations
        based *strictly* on the processed sales and refund data provided. Focus on high-selling items, items with high refunds, and potential profitability issues.
      5.The report should in Arabic Language.
      6.The currency money MAD (Morcocco Dirham)
    Use the available tools to fetch the necessary data. If a date is specified in the user request, use that date for the tools. Otherwise, use the default (current month). You may need to call multiple tools.
        """

        # Start a chat session for multi-turn conversation
        chat = model.start_chat(enable_automatic_function_calling=False) # We handle calls manually

        # Send the initial prompt
        response = chat.send_message(initial_prompt, tools=tools)

        # --- Store fetched data ---
        # Use dictionaries to store results keyed by function name for easier access
        fetched_data = {}

        # --- Loop to handle function calls ---
        while response.candidates and response.candidates[0].content.parts:
            function_call_parts = [part for part in response.candidates[0].content.parts if part.function_call]

            if not function_call_parts:
                break

            api_tool_responses = []
            for part in function_call_parts:
                function_call = part.function_call
                function_name = function_call.name
                args = dict(function_call.args)
                print(f"AI requested function call: {function_name} with args: {args}")

                function_response_content = None
                api_tool_response_part = None

                try:
                    date_str = args.get('date', None)
                    target_date = None
                    if date_str:
                        try:
                            target_date = datetime.strptime(date_str, '%Y-%m')
                        except ValueError:
                            print(f"Warning: Could not parse date '{date_str}'. Using current month.")
                            target_date = datetime.now()
                    else:
                        target_date = datetime.now()

                    # --- Execute function and store result ---
                    result_data = None # Variable to hold the raw result
                    if function_name == "get_sales_data":
                        result_data = reporting.get_sales_data(date=target_date)
                        fetched_data['sales'] = result_data # Store sales data
                        function_response_content = json.dumps(result_data)
                    elif function_name == "get_refunds_data":
                        result_data = reporting.get_refunds_data(date=target_date)
                        fetched_data['refunds'] = result_data # Store refund data
                        function_response_content = json.dumps(result_data)
                    else:
                        print(f"Error: Unknown function call requested: {function_name}")
                        function_response_content = json.dumps({"error": f"Unknown function: {function_name}"})

                    # --- Prepare the response part for this specific function call ---
                    api_tool_response_part = glm.Part(
                        function_response=glm.FunctionResponse(
                            name=function_name,
                            response={'content': function_response_content}
                        )
                    )

                except Exception as e:
                    print(f"Error executing function {function_name}: {str(e)}")
                    # Send an error back for this specific function call
                    api_tool_response_part = glm.Part(
                        function_response=glm.FunctionResponse(
                            name=function_name,
                            response={'content': json.dumps({"error": f"Failed to execute function: {str(e)}"}) }
                        )
                    )

                if api_tool_response_part:
                    api_tool_responses.append(api_tool_response_part)

            if api_tool_responses:
                print(f"Sending {len(api_tool_responses)} function response(s) back to AI.")
                response = chat.send_message(api_tool_responses, tools=tools)
            else:
                print("Error: No API tool responses generated despite function calls.")
                break
        # --- End of loop ---

        # --- Generate Pareto Chart ---
        pareto_chart_path = None
        # Check if sales data was fetched successfully
        if 'sales' in fetched_data and fetched_data['sales'] and 'sales data' in fetched_data['sales']:
            try:
                # Pass the list of sales dictionaries to the reporting function
                pareto_chart_path = reporting.generate_monthly_sales_pareto(fetched_data['sales']['sales data'])
            except Exception as e:
                print(f"Error generating Pareto chart: {e}") # Log error if chart generation fails

        # --- Prepare final context ---
        final_report_text = ""
        if response.text:
            final_report_text = response.text
            print("AI finished function calls and provided final report.")
        else:
            # Handle cases where AI didn't provide text (e.g., error, stopped)
            print("Error: AI did not provide a final text response after function calls.")
            if response.candidates and response.candidates[0].finish_reason != 'STOP':
                 print(f"AI stopped unexpectedly. Reason: {response.candidates[0].finish_reason}")
                 # Optionally add error message to report or return JsonResponse
                 final_report_text = f"\n\n*Error: AI processing stopped unexpectedly ({response.candidates[0].finish_reason}). Report may be incomplete.*"
            else:
                 final_report_text = "\n\n*Error: AI did not generate the final report text.*"


        context = {
            'report_markdown': final_report_text,
            'pareto_chart_path': pareto_chart_path # Add chart path to context
        }
        return render(request, 'dashboard/report_template.html', context)

    except Exception as e:
        print(f"Error in ai_report_generator: {str(e)}")
        # Consider more specific error handling based on exception type
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


@csrf_exempt
def ai_report_the_inventory(request):
    """Handles user prompts and interacts with the Gemini API using a loop for function calls."""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        # Define the tools the AI can use
        tools = [
            glm.Tool(
                function_declarations=[
                    glm.FunctionDeclaration(
                        name="get_the_sales_data",
                        description="Fetches sales data for items in the subclass 'The' for a specified month and year. If no date is provided, it defaults to the current month. Returns a list of sales records including date, item ID, item name, quantity sold, selling price, and cost price.",
                        parameters=glm.Schema(
                            type=glm.Type.OBJECT,
                            properties={
                                'date': glm.Schema(type=glm.Type.STRING, description="Optional. The date (YYYY-MM) for which to retrieve sales data. E.g., '2023-10'.")
                            },
                            required=[]
                        )
                    ),
                    glm.FunctionDeclaration(
                        name="get_the_data",
                        description="Retrieves the current stock information for items belonging to the subclass 'The'. Includes item ID, name, description, price, reference, and weight.",
                        parameters=glm.Schema(
                            type=glm.Type.OBJECT,
                            properties={
                                'id': glm.Schema(type=glm.Type.NUMBER, description="Primary key  "),
                                'name':glm.Schema(type=glm.Type.STRING, description="name of The item"),
                                'description':glm.Schema(type=glm.Type.STRING, description="description of The item"),
                                'price':glm.Schema(type=glm.Type.NUMBER,description="price cost"),
                                'ref':glm.Schema(type=glm.Type.STRING),
                                'weight':glm.Schema(type=glm.Type.STRING),
                            },
                            required=[]
                        )
                    ),
                    glm.FunctionDeclaration(
                        name="get_the_purchass_data",
                        description="Retrieves purchase order data for items in the subclass 'The'. Collects information such as date of purchase, receipt ID, item ID, item name, quantity purchased, and cost price.",
                        parameters=glm.Schema(
                            type=glm.Type.OBJECT,
                            properties={
                                'date': glm.Schema(type=glm.Type.STRING, description="Optional. The date (YYYY-MM) for which to retrieve purchase data. E.g., '2023-10'."),
                                'receipt_id': glm.Schema(type=glm.Type.NUMBER, description="Receipt item ID "),
                                'item_id': glm.Schema(type=glm.Type.NUMBER, description="Primary key of The item "),
                                'item_name':glm.Schema(type=glm.Type.STRING, description="name of The item"),
                                'quantity PurchaseOrder':glm.Schema(type=glm.Type.NUMBER, description="description of quantity purchasing The item"),
                                'cost_price':glm.Schema(type=glm.Type.NUMBER,description="price cost"),
                            },
                            required=[]
                        )
                    ),
                     glm.FunctionDeclaration(
                         name="get_lead_time",
                         description="Retreive lead time for each items ins stock",
                         parameters=glm.Schema(
                             type=glm.Type.OBJECT,
                             properties={},
                             required=[]
                         )
                        
                    )  
                ]
            )
        ]
        prompt=""""### AI Agent Responsibilities:
        *The goal is optimizaing inventory.
        I would like to generate a report focusing on the items in the subclass "The" for the current month. Please proceed with the following steps:

        1. **Current Month**: Use the current month as the default date for the report.

        2. **Function Calls**:
        - Use the `get_the_data` function to retrieve a list of items in the subclass "The." This should include:
            - Item ID
            - Name
            - Description
            - Current stock levels
            - Selling price
            - Cost price
            - Reference
            - Weight
            **What are the quantity optimal stock for each items You can describe as Table .
            
        - Use the `get_the_sales_data` function to retrieve sales data for items in the subclass "The" for the current month. This should include:
            - Total sales amount
            - Quantity sold
            - Breakdown of sales by item

        3. **Refund Data**: Note that I do not require refund data for this report.

        4. **Insights and Recommendations**: Based on the retrieved sales data, provide insights into which items are selling well and suggest optimizing stock levels accordingly.
           To estimate the optimal stock levels, we need to consider sales volume, lead time, and a safety stock buffer. A simple approach:

            1.  **Calculate Average Daily Sales:** Divide the total quantity sold this month by the number of days in the month.
            2.  **Calculate Lead Time Demand:** Multiply the average daily sales by the lead time.
            3.  **Determine Safety Stock:** This is a buffer to cover unexpected demand surges. A common method is to use a percentage of the lead time demand (e.g., 20-30%).
            4.  **Optimal Stock Level:** Lead Time Demand + Safety Stock.

        5. **Visualizations**: Recommend visualizations to illustrate the sales data, such as bar charts for sales quantities or pie charts for sales percentages.
        Please generating the data tables using the `get_the_data` and `get_the_sales_data` and `get_lead_time` functions. Thank you!
                        
        """      
        # Start a chat session for multi-turn conversation
        chat = model.start_chat(enable_automatic_function_calling=False) # We handle calls manually

        # Send the initial prompt
        response = chat.send_message(prompt, tools=tools)

        # --- Store fetched data ---
        # Use dictionaries to store results keyed by function name for easier access
        fetched_data = {}

        # --- Loop to handle function calls ---
        while response.candidates and response.candidates[0].content.parts:
            function_call_parts = [part for part in response.candidates[0].content.parts if part.function_call]

            if not function_call_parts:
                break

            api_tool_responses = []
            for part in function_call_parts:
                function_call = part.function_call
                function_name = function_call.name
                args = dict(function_call.args)
                print(f"AI requested function call: {function_name} with args: {args}")

                function_response_content = None
                api_tool_response_part = None

                try:
                    date_str = args.get('date', None)
                    target_date = None
                    if date_str:
                        try:
                            target_date = datetime.strptime(date_str, '%Y-%m')
                        except ValueError:
                            print(f"Warning: Could not parse date '{date_str}'. Using current month.")
                            target_date = datetime.now()
                    else:
                        target_date = datetime.now()

                    # --- Execute function and store result ---
                    result_data = None # Variable to hold the raw result
                    #The sales
                    if function_name == "get_the_sales_data":
                        result_data = reporting.get_the_sales_data_asList(date=target_date)
                        fetched_data['the_sales'] = result_data # Store sales data
                        function_response_content = json.dumps(result_data)
                    #Refunds The    
                    elif function_name == "get_refunds_data":
                        result_data = reporting.get_refunds_data(date=target_date)
                        fetched_data['refunds'] = result_data # Store refund data
                        function_response_content = json.dumps(result_data)
                    #The Data    
                    elif function_name =="get_the_data":
                        result_data=reporting.get_the_data()  
                        fetched_data['The'] = result_data
                        function_response_content=json.dumps(result_data)
                    elif function_name=="get_the_purchass_data":
                        result_data=reporting.get_the_purchass_data()  
                        fetched_data['the purchass']=result_data  
                        function_response_content=json.dumps(result_data)
                    elif function_name=="get_lead_time":
                        result_data=reporting.get_lead_time() 
                        fetched_data['lead_time']=result_data  
                        function_response_content=json.dumps(result_data)    
                    else:
                        print(f"Error: Unknown function call requested: {function_name}")
                        function_response_content = json.dumps({"error": f"Unknown function: {function_name}"})

                    # --- Prepare the response part for this specific function call ---
                    api_tool_response_part = glm.Part(
                        function_response=glm.FunctionResponse(
                            name=function_name,
                            response={'content': function_response_content}
                        )
                    )

                except Exception as e:
                    print(f"Error executing function {function_name}: {str(e)}")
                    # Send an error back for this specific function call
                    api_tool_response_part = glm.Part(
                        function_response=glm.FunctionResponse(
                            name=function_name,
                            response={'content': json.dumps({"error": f"Failed to execute function: {str(e)}"}) }
                        )
                    )

                if api_tool_response_part:
                    api_tool_responses.append(api_tool_response_part)

            if api_tool_responses:
                print(f"Sending {len(api_tool_responses)} function response(s) back to AI.")
                response = chat.send_message(api_tool_responses, tools=tools)
            else:
                print("Error: No API tool responses generated despite function calls.")
                break
        # --- End of loop ---
        # generate Bar chart
        bar_chart_path = None
        pie_chart_path = None
        if 'the_sales' in fetched_data:
            try:
                # Pass the list of sales dictionaries to the reporting function
                bar_chart_path = reporting.generate_sales_quantity_bar_chart(fetched_data['the_sales'])
                pei_chart_path = reporting.generate_sales_percentage_by_item_pie_chart(fetched_data['the_sales'])
            except Exception as e:
                print(f"Error generating Pareto chart: {e}")

        final_report_text = ""
        if response.text:
            final_report_text = response.text
            print("AI finished function calls and provided final report.")
        else:
            # Handle cases where AI didn't provide text (e.g., error, stopped)
            print("Error: AI did not provide a final text response after function calls.")
            if response.candidates and response.candidates[0].finish_reason != 'STOP':
                 print(f"AI stopped unexpectedly. Reason: {response.candidates[0].finish_reason}")
                 # Optionally add error message to report or return JsonResponse
                 final_report_text = f"\n\n*Error: AI processing stopped unexpectedly ({response.candidates[0].finish_reason}). Report may be incomplete.*"
            else:
                 final_report_text = "\n\n*Error: AI did not generate the final report text.*"


        context = {
            'report_markdown': final_report_text,
            'bar_chart_path':bar_chart_path,
            'pie_chart_path':pei_chart_path

        }
        return render(request, 'dashboard/the_inventory_report.html', context)
        
    except Exception as e:
        print(f"Error in ai_report_generator: {str(e)}")
        # Consider more specific error handling based on exception type
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)  
 