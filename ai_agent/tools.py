import asyncio 
from google.genai import types
from django.conf import settings
import os
import logging
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
import google.generativeai as genai




    