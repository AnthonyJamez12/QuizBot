from django.db import models

class Topic(models.Model):
    """
    Represents a network security topic for focused quizzes.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class QuizQuestion(models.Model):
    """
    Stores quiz questions, which can be multiple choice, true/false, or open-ended.
    """
    QUESTION_TYPES = [
        ('MC', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('OE', 'Open-ended')
    ]

    text = models.TextField()
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES)
    topic = models.ForeignKey(Topic, related_name="questions", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.text} ({self.get_question_type_display()})"

class AnswerOption(models.Model):
    """
    Stores options for multiple choice and true/false questions.
    """
    question = models.ForeignKey(QuizQuestion, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Option: {self.text} (Correct: {self.is_correct})"

class UserResponse(models.Model):
    """
    Logs responses from users for each question to enable feedback and scoring.
    """
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, null=True, blank=True, on_delete=models.SET_NULL)
    open_ended_response = models.TextField(null=True, blank=True)
    correct = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  

    def evaluate_open_ended(self, correct_keywords):
        """
        Basic method to evaluate open-ended responses based on keywords.
        For open-ended questions, matches keywords and assigns score or correct status.
        """
        if self.question.question_type == 'OE' and self.open_ended_response:
            response_lower = self.open_ended_response.lower()
            self.correct = any(keyword.lower() in response_lower for keyword in correct_keywords)
            self.score = 1.0 if self.correct else 0.0
            self.save()
