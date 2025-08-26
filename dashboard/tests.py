from django.test import TestCase
from .views import inventory_report
# from ai_agent.agent import root_agent
from ai_agent.tools import call_db_agent, call_ds_agent
from ai_agent.prompts import return_instructions_root   
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from google.adk.agents import Agent
from ai_agent.tools import call_db_agent, call_ds_agent
from ai_agent.prompts import return_instructions_root
import sys
import pytest
import unittest

from datetime import date
import pytest
from django.test import TestCase

@pytest.mark.django_db

class TestInventoryAIReport(TestCase):
    def test_inventory_report_view(self):
        
        response = Client().get(reverse('dashboard:inventory_report'))#Set up and Act 
        
        date_today = date.today()

        root_agent = Agent(
            name="root_agent",
            description="Root agent for data agent multi-agents.",
            instructions=return_instructions_root,
            tools=[],
            # artifacts=load_artifacts("ai_agent/artifacts/root_agent_artifacts.json"),
            session_service=None,  # Set in the test or main application
            artifact_service=None,  # Set in the test or main application
            app_name="state_app_manual",
            user_id="user2",
            session_id="session2",
            state={"user:login_count": 0, "task_status": "idle"},
        )

        self.assertEqual(response.status_code, 200)#Assert that the response status code is 200 OK
        self.assertTemplateUsed(response, 'dashboard/inventory_report.html')

    