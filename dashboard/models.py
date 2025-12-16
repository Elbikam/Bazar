from django.db import models


from django.db import models

class ChatMessage(models.Model):
    # This defines the DATA STRUCTURE
    SENDER_CHOICES = [
        ('USER', 'User'),
        ('AI', 'AI Agent'),
    ]
    
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()  # The text payload
    timestamp = models.DateTimeField(auto_now_add=True) # Temporal tracking

    def __str__(self):
        return f"{self.sender}: {self.content[:20]}..."