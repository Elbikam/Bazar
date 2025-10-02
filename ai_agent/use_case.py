from .service_agent import ServiceAgent
import asyncio



class CallAgent:
    def __init__(self,service:ServiceAgent):
        self.service = service
    async def send_message(self,prompt):
        result = await self.service.sendMessage(prompt)
        return result
