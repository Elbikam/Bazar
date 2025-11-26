import pytest
from ai_agent.interface import ServiceAgent
from ai_agent.agent import call_root_agent
import json 


class TestIntegrationServiceAgentWithAPI:
    @pytest.mark.asyncio 
    async def test_intergaret_service_agent_with_API(self):
        query = "hi,how are you?"
        events = await call_root_agent(query)
        service_agent = ServiceAgent(events)
        response_txt = await service_agent.full_response_text()
        assert response_txt == "I am doing well, thank you for asking. How can I help you with SQL queries today?"

       
        