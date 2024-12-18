from django.contrib.auth.models import User
from django.db import models


class profile1(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    photo1 = models.ImageField(upload_to='user_images/', null=True, blank=True)
    photo2 = models.ImageField(upload_to='user_images/', null=True, blank=True)
    photo3 = models.ImageField(upload_to='user_images/' , null=True, blank=True)
    interest1 = models.CharField(max_length=50, blank=True, null=True)
    interest2 = models.CharField(max_length=50, blank=True, null=True)
    interest3 = models.CharField(max_length=50, blank=True, null=True)
    interest4 = models.CharField(max_length=50, blank=True, null=True)
    interest5 = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    target_user = models.ForeignKey(profile1, on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=10, choices=(('like', 'Like'), ('dislike', 'Dislike')))
    created_at = models.DateTimeField(auto_now_add=True, null=True)




class Notification(models.Model):
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_notifications', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.recipient} from {self.sender}"





class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='user_images', blank=True, null=True)  
    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}: {self.content[:20]}"


