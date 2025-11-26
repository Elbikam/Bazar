import pytest
from unittest.mock import patch,MagicMock,AsyncMock
from django.test import TestCase
from dashboard.report import GetDataFromAI
from ai_agent.interface import ServiceAgent
from ai_agent.agent import GeminiAPI
from dashboard.test_dashboard.fake_ai_response import fake_ai_response
class TestGetDataFromAI:
    @patch('dashboard.report.ServiceAgent')
    @pytest.mark.asyncio
    async def test_call_agent(self,mock_service_agent):
        mock_service_agent.full_response_text = AsyncMock()
        mock_service_agent.full_response_text.return_value = "im doing well.thanks for asking"
        query = "Hi,how are you today?"
        get_data = GetDataFromAI(mock_service_agent)
        response = await get_data.call_agent(query)
        assert response == "im doing well.thanks for asking"
        

class TestGenerateReport(TestCase):
    @patch('dashboard.views.GetDataFromAI')
    def test_display_chart(self,mock_call_agent):
        mock_call_agent.call_agent = AsyncMock()
        mock_call_agent.call_agent.return_value = fake_ai_response
        