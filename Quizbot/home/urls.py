from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_menu_screen, name='main_menu'),
    path('topics/', views.topic_menu_screen, name='topic_menu'),
    path('quiz/<str:quiz_type>/', views.quiz_screen, name='quiz_screen'),
    path('quiz/<str:quiz_type>/<int:topic_id>/', views.quiz_screen, name='quiz_screen_topic'),
    path('submit_answer/', views.submit_answer, name='submit_answer'),
]
