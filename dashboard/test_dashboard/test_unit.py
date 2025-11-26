import pytest
from unittest.mock import patch,MagicMock,AsyncMock

from sqlalchemy.orm import query
from dashboard.report import GetDataFromAI
from ai_agent.interface import ServiceAgent
from ai_agent.agent import GeminiAPI

class TestGetDataFromAI:
    @pytest.mark.asyncio
    async def test_call_agent(self):
        query = "Hi,how are you today?"
        gemini = GeminiAPI()
        service_agent = ServiceAgent(gemini)
        get_data = GetDataFromAI(service_agent)
        response = await get_data.call_agent(query)
        
