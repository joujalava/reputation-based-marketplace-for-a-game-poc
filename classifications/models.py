from django.db import models

class Classification(models.Model):
    name = models.TextField(max_length=50, primary_key=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True)
    has_picture = models.BooleanField(default=False)
    has_crafts = models.BooleanField(default=False)

    def __str__(self):
        return self.name