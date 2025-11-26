
from ai_agent.interface import ServiceAgent
from typing import Optional
from asgiref.sync import sync_to_async 

class GetDataFromAI:
    def __init__(self,service_agent:ServiceAgent) -> None:
        self.service_agent = service_agent
    async def call_agent(self,query):
        result = await self.service_agent.full_response_text(query)
        return result 
        


