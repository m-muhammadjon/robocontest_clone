from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('users', views.users, name='users'),
    path('profile/<str:username>', views.user_profile, name='profile'),
    path('profile/<str:username>/attempts', views.user_attempts, name='attempts'),
    path('profile/<str:username>/tasks', views.user_solved_tasks, name='solved_problems')
]
