from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=255)
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)  # Make sure this exists
    level = models.CharField(max_length=10)


    def __str__(self):
        return self.question_text
from django.db import models
from django.contrib.auth.models import User

class Results(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    correct_answers = models.IntegerField()
    wrong_answers = models.IntegerField()
    total_questions = models.IntegerField()
    easy_questions = models.IntegerField()
    medium_questions = models.IntegerField()
    hard_questions = models.IntegerField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}'s Results on {self.date_submitted}"
