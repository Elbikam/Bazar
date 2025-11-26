"""Test cases for the analytics agent and its sub-agents."""
import json
from unittest.mock import patch,MagicMock,AsyncMock
from numpy import full
import pytest
from ai_agent.agent import GeminiAPI

from ai_agent.interface import ServiceAgent



class TestServiceAgent():

    @pytest.mark.asyncio 
    async def test_strem_event(self):
        query = "hi,how are u?"
        gemini = GeminiAPI()
        service_agent = ServiceAgent(gemini)
        response = await service_agent.full_response_text(query)
        assert response == "I am doing well, thank you for asking. How can I help you today?"


        