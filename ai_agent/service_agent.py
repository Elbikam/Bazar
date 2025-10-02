from abc import ABC
from ai_agent.agent import call_root_agent
import asyncio
import requests
import google.generativeai as genai
from django.conf import settings
import httpx
import os
from dotenv import load_dotenv

load_dotenv() 
# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

async def mock_call_adk(prompt: str):
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": settings.GEMINI_API_KEY  # Use X-goog-api-key instead of Authorization
    }
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url=api_url, json=payload, headers=headers)
        if response.status_code == 401:
            raise ValueError(f"Unauthorized: Check your API key and permissions. API Key: {settings.GEMINI_API_KEY}")
        elif response.status_code != 200:
            raise ValueError(f"API Error: {response.status_code} - {response.text}")
        return response.json()


class IService(ABC):
    def sendMessage(prompt):
        pass
    def receiveMessage(prompt):
        pass
    def connect():
        pass
    def getSensorData(prompt):
        pass
    def readEnvironment(prompt):
        pass
    def performAction(prompt):
        pass
    def executeTask(prompt):
        pass
    def saveState(prompt):
        pass
    def loadState(prompt):
        pass
    def wait(prompt):
        pass
    

class ServiceAgent(IService): 
    def __init__(self):
        pass
    async def sendMessage(self,prompt):
        result = await mock_call_adk(prompt)
        return result