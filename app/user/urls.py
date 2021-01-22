from django.urls import path, include
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.UserCreateAPIView.as_view(), name='create')
]