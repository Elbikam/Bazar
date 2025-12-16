import pytest 
import json
from django.test import TestCase, Client
from unittest.mock import MagicMock, patch, AsyncMock
from dashboard.models import ChatMessage

# Systems Engineering: This is our Test Bench
class ChatIntegrationTest(TestCase):

    def setUp(self):
        # 1. Setup the Client (The Browser Simulator)
        self.client = Client()
        self.url = '/dashboard/chat_api/'

    @patch('dashboard.views.ControleConversation.call_agent')
    def test_full_conversation_flow(self, mock_call_agent):
        """
        Integration Scenario:
        1. User sends "Hello".
        2. System saves User msg to DB.
        3. System calls AI (Mocked).
        4. System saves AI msg to DB.
        5. System returns JSON.
        """
        
        # --- PHASE 1: PREPARE THE FAKE BEHAVIOR ---
        # We tell the mock: "When called, wait a bit, then return this string"
     
        mock_call_agent.return_value = 'I am the Test AI'


        # --- PHASE 2: EXECUTE (The Stimulus) ---
        payload = {"message": "Hello World"}
        response = self.client.post(
            self.url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )

        # --- PHASE 3: VERIFY (The Inspection) ---
        
        # Check A: Did the View return success? (Interface Check)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['ai_response'], "I am the Test AI")

        # Check B: Did the Orchestrator call the AI? (Behavioral Check)
        mock_call_agent.assert_called_once_with("Hello World")

       






