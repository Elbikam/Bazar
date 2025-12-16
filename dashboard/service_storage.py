
from .models import ChatMessage

class ServiceStorage():
    def save_message(self,sender,content):
        message = ChatMessage.objects.create(sender=sender,content=content)
        