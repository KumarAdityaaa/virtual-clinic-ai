from django.db import models

from server.models import Account


class CopilotConversation(models.Model):
    account = models.ForeignKey(
        Account,
        related_name="copilot_conversations",
        on_delete=models.CASCADE
    )
    title = models.CharField(
        max_length=200,
        default="New Chat"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated"]

    def __str__(self):
        return self.title


class CopilotMessage(models.Model):
    conversation = models.ForeignKey(
        CopilotConversation,
        related_name="messages",
        on_delete=models.CASCADE
    )
    role = models.CharField(
        max_length=20
    )
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
