from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.UserCreateAPIView.as_view(), name='create'),
    path('update/', views.UserProfileUpdateAPIView.as_view(), name='update'),
    path('token/', views.UserTokenAPIView.as_view(), name='token'),
]
