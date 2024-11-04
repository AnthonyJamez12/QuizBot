from django.contrib import admin
from .models import Topic, QuizQuestion, AnswerOption, UserResponse

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type', 'topic')
    list_filter = ('question_type', 'topic')
    search_fields = ('text',)
    ordering = ('topic',)

@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text',)

@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('question', 'selected_option', 'open_ended_response', 'correct', 'score')
    list_filter = ('correct',)
    search_fields = ('open_ended_response',)
    ordering = ('question',)
