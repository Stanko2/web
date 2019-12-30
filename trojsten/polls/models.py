from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone


class Question(models.Model):
    text = models.CharField(max_length=1000)
    created_date = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField(default=datetime(2020, 12, 31, 23, 59, 59))

    def __str__(self):
        return self.text


class Answer(models.Model):
    text = models.CharField(max_length=1000)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)

    def __str__(self):
        return f'Answer "{self.text}" to question "{str(self.question)}"'


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    answer = models.ForeignKey("Answer", on_delete=models.CASCADE)

    def __str__(self):
        return f'Vote for "{str(self.answer)}"'
