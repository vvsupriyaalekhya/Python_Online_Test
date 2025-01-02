import csv
from quiz.models import Question  # replace `quiz` with your app name
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Import questions from CSV file'

    def handle(self, *args, **kwargs):
        with open('C:\\Users\\Verukonda Supriya\\OneDrive\\Desktop\\quiz_project\\dataset.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Question.objects.create(
                    question_text=row['Question'],
                    option_a=row['Option A'],
                    option_b=row['Option B'],
                    option_c=row['Option C'],
                    option_d=row['Option D'],
                    answer=row['Answer'],
                    level=row['Level']
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported questions'))
