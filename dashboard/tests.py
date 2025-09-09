from django.test import TestCase,Client
from .views import inventory_report
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from google.adk.agents import Agent
import sys
import pytest
from  unittest import mock

from datetime import date
import pytest
from django.test import TestCase

from dashboard.views import generate_sales_report_view

from ai_agent.agent import call_orchestrator_agent
from django.urls import reverse



class TestGenerateAIReport(TestCase):
    def setUp(self):
        self.client = Client()

    def test_sales_report_view(self):
        query = "query test"
        call_orchestrator_agent = mock.Mock()
        call_orchestrator_agent.return_value = "mock result"
        response = call_orchestrator_agent(query)
        self.assertEqual(response ,"mock result" )
    def test_plug_in_result_html(self):
        response = self.client.get(reverse('dashboard:sales_report')) 
        # Assert the HTTP status code
        self.assertEqual(response.status_code, 200)

        # Assert that a specific template was used
        self.assertTemplateUsed(response, 'dashboard/sales_report.html')

        # Assert that the response content contains expected text
        self.assertContains(response, "test")
    
