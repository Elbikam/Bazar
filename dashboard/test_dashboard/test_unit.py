import pytest
from unittest.mock import patch,MagicMock,AsyncMock
from django.test import TestCase
from dashboard.report import GetDataFromAI
from ai_agent.interface import ServiceAgent
from ai_agent.agent import GeminiAPI
from dashboard.service_storage import ServiceStorage
from dashboard.models import ChatMessage
from django.test import Client
from dashboard.views import ControleConversation
class TestGetDataFromAI:
    @patch('dashboard.report.ServiceAgent')
    @pytest.mark.asyncio
    async def test_call_agent(self,mock_service_agent):
        mock_service_agent.full_response_text = AsyncMock()
        mock_service_agent.full_response_text.return_value = "im doing well.thanks for asking"
        query = "Hi,how are you today?"
        get_data = GetDataFromAI(mock_service_agent)
        response = await get_data.call_agent(query)
        assert response == "im doing well.thanks for asking"
        

class TestGenerateReport(TestCase):
    @patch('dashboard.views.GetDataFromAI')
    def test_display_chart(self,mock_call_agent):
        mock_call_agent.call_agent = AsyncMock()

        

        
class TestStorageService(TestCase):
    def setUp(self):
        ChatMessage.objects.create(sender='B',content='Hi')

    def test_save_message(self):
        msg = ChatMessage.objects.get(sender='B')
        self.assertEqual(msg.sender,'B')


class TestChatView(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
    def test_chat_page(self):
        response = self.client.get('/dashboard/chat_page')  
        self.assertEqual(response.status_code, 200)

class TestControleConverstaion():
    @patch('dashboard.views.ServiceAgent')
    @patch('dashboard.views.ServiceStorage')
    @pytest.mark.asyncio
    async def test_save_user_query(self,mock_db,mock_agent):
        user = 'boubaker'
        content = 'hi how are?'
        mock_db.save_message = MagicMock()
        mock_db.save_message.return_value = f'message is saved'
        mock_agent.full_response_text=AsyncMock()
        mock_agent.full_response_text.return_value = "Im fine thanks"
        what_expected_save_content_and_role = f'message is saved'
        what_expected_call_agent = "Im fine thanks"
       
        conversation = ControleConversation(mock_db,mock_agent)
        what_actually_happened = conversation.save_role_and_content(user,content)
        what_actually_happened_call_agent = await conversation.call_agent(content)
        assert what_actually_happened == what_expected_save_content_and_role
        assert what_actually_happened_call_agent == what_expected_call_agent 

class TestChatAPI(TestCase):
    def setUp(self) -> None:
        self.client = Client()
    def test_chat_api(self):
        response = self.client.get('/dashboard/chat_api')
        self.assertEqual(response.status_code,301)