from django.db import models

# Create your models here.
class Contact(models.Model):
    email = models.EmailField()
    message = models.TextField()
    problem = models.TextField()
    query_date = models.DateTimeField(auto_now_add=True)
    
class Chathistory(models.Model):
    user_message= models.TextField()
    teknixtic_response= models.TextField()
    date= models.DateTimeField(auto_now_add=True)


class ChatSession(models.Model):

    title = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ChatMessage(models.Model):

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE
    )

    role = models.CharField(max_length=20)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} - {self.content[:30]}"





          