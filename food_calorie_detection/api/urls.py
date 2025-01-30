from django.urls import path
from . import views
from .views import DetectView, LoginView,CheckAuthView, RegisterView, LogoutView

urlpatterns = [
    path('detect/', DetectView.as_view(), name='detect'),
    path('login/', LoginView.as_view(), name='login'),
    path('check-auth/', CheckAuthView.as_view(), name='check_auth'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

