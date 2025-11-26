# myproject/utils/fake_data.py

from unittest.mock import Mock

def create_fake_gemini_response_object():
    """
    Generates a realistic mock object that mimics the nested structure
    of the google.genai.types.GenerateContentResponse SDK object,
    including data for both text summary and chart data.
    """
    
    # 1. Define the raw data you want the template to eventually use
    # We use a JSON string format here, as if the AI returned it in JSON mode
    structured_json_output = """
    {
      "summary_text": "Sales performance improved significantly in Q3, driven by new product launches.",
      "chart_title": "Quarterly Sales Data",
      "sales_data": [
        {"month": "Jan", "revenue": 1000},
        {"month": "Feb", "revenue": 2500},
        {"month": "Mar", "revenue": 1500},
        {"month": "Apr", "revenue": 4000}
      ]
    }
    """
    
    # 2. Build the nested Mock object structure
    
    # The innermost part is the actual text/JSON string
    part_mock = Mock()
    part_mock.text = structured_json_output
    
    # This sits inside the 'content' part
    content_mock = Mock()
    content_mock.parts = [part_mock]
    
    # This sits inside the 'candidates' list
    candidate_mock = Mock()
    candidate_mock.content = content_mock
    
    # The top-level response object
    response_mock = Mock()
    response_mock.candidates = [candidate_mock]
    
    # The SDK often provides a simple .text accessor for convenience
    response_mock.text = structured_json_output
    
    return response_mock


import json

def parse_gemini_response_to_dict(gemini_response_object):
    """
    Takes the raw SDK response object and extracts the JSON string, 
    returning a clean Python dictionary for the Django view.
    """
    # Access the deeply nested text attribute of the mock object:
    json_string = gemini_response_object.candidates[0].content.parts[0].text
    
    # Parse the JSON string into a usable Python dictionary
    return json.loads(json_string)

CLEAN_REPORT_DATA_DICT = {
    "summary_text": "Sales performance improved significantly in Q3, driven by new product launches.",
    "chart_title": "Quarterly Sales Data",
    "sales_data": [
        {"month": "Jan", "revenue": 1000},
        {"month": "Feb", "revenue": 2500},
        {"month": "Mar", "revenue": 1500},
        {"month": "Apr", "revenue": 4000}
    ]
}
