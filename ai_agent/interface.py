from abc import ABC,abstractmethod
from ai_agent.agent import GeminiAPI
import asyncio


import json 

class InterfaceAgent(ABC):
    @abstractmethod
    async def full_response_text(self):
        pass
class ServiceAgent(InterfaceAgent):
    def __init__(self,gemini:GeminiAPI) -> None:
        self.gemini  = gemini 
    
    async def full_response_text(self, query):
        final_text = ""
            
            # Call the API
        events = await self.gemini.call_root_agent(query)
            
        async for event in events:
            if event.is_final_response():
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            # Accumulate in case the final response is also streamed in chunks
                            final_text += part.text
        return final_text      