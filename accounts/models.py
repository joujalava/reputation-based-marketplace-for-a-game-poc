from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    reputation = models.IntegerField(default=0)
    character_name = models.CharField(max_length=100, blank=True)

@receiver(post_save, sender=User)
def create_reputation(sender, instance, created, **kwargs):
    if created:
        reputation = Profile(user=instance)
        reputation.save()