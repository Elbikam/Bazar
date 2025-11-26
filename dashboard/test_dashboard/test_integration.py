# import pytest 
# from django.test import TestCase, RequestFactory, AsyncRequestFactory
# from unittest.mock import patch, AsyncMock, MagicMock

# from dashboard.views import GenerateReport

# import json


# class ReportViewIntegrationTest(TestCase):
#     """
#     Integration tests for the GenerateReport view.
#     Tests the view's interaction with the AI agent service.
#     """
     
#     def setUp(self):
#         """Setup method called before each test."""
#         self.factory = AsyncRequestFactory()
#         self.query = "hi how are you?"

    
#     @patch("dashboard.views.GetDataFromAI")
#     async def test_report_views_integration(self, mock_call_root_agent):
#         """
#         Test that GenerateReport view correctly calls the AI agent and renders HTML template.
#         """
#         # Setup: Configure the mock to return the expected response format
#         # call_root_agent returns a dict with 'summary' key (as per agent.py)
#         # ServiceAgent will parse this and return just the summary string
#         expected_summary = 'Sales performance improved significantly in Q3, driven by new product launches.'
#         expected_ai_response = {
#             'summary': expected_summary
#         }
#         # Configure the async mock to return the expected response
#         # Since call_root_agent is async, we use return_value which will be awaited
        
#         mock_call_root_agent.return_value = expected_ai_response

#         # Execute: Make a GET request to the view with a query parameter
#         request = self.factory.get("/dashboard/report_detail", {'query': self.query})
#         response =  await GenerateReport.as_view()(request)
       
#         self.assertEqual(response.status_code, 200)

        
    
#     @patch("dashboard.views.GetDataFromAI")
#     async def test_report_views_integration_default_query(self, mock_call_root_agent):
#         """
#         Test that GenerateReport view uses default query when none is provided.
#         """
#         # Setup: Configure the mock
#         expected_ai_response = {"report_data": "Default report generated successfully."}
#         mock_call_root_agent.call_root_agent= MagicMock()
#         mock_call_root_agent.call_root_agent.return_value = expected_ai_response

#         # Execute: Make a GET request without query parameter
#         request = self.factory.get("/dashboard/report_detail")
#         response = await GenerateReport.as_view()(request)

#         # Assert: Verify the response
#         assert response.status_code == 200
        
#         # Verify it's an HTML response
#         assert 'text/html' in response.get('Content-Type', '')
        
#         response_content = response.content.decode('utf-8')
        
#         assert expected_ai_response['report_data'] in response_content
        
    
#     @patch("dashboard.report.GetDataFromAI.call_root_agent")
#     async def test_report_views_integration_with_chart_data(self, mock_call_root_agent):
#         """
#         Test that GenerateReport view handles response with chart data in JSON format.
#         Note: If AI returns JSON string, the view will try to parse it.
#         """
#         # Setup: Configure the mock to return a dict (call_root_agent format)
#         # The summary contains JSON string that the view will parse
#         json_string = json.dumps({
#             'summary': 'Sales report with chart data',
#             'chart_data': [
#                 {'label': 'Jan', 'value': 1000},
#                 {'label': 'Feb', 'value': 2500}
#             ]
#         })
#         # call_root_agent returns dict with 'summary' key containing the JSON string
#         expected_ai_response = {'summary': json_string}
#         mock_call_root_agent.return_value = expected_ai_response

#         # Execute: Make a GET request
#         request = self.factory.get("/dashboard/report_detail", {'query': self.query})
#         response = await GenerateReport.as_view()(request)

#         # Assert: Verify the response
#         assert response.status_code == 200
#         response_content = response.content.decode('utf-8')
#         # The view should parse the JSON and extract the summary
#         assert 'Sales report with chart data' in response_content
        

        










