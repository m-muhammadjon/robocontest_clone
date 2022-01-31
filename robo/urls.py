from django.urls import path

from . import views

app_name = 'robo'

urlpatterns = [
    path('tasks', views.task_list, name='tasks'),
    path('tasks/<int:number>',views.task_detail, name='task'),
    path('tasks/<int:number>/attempts', views.task_attempts, name='task_attempts'),
    path('attempts', views.attempts, name='attempts'),
    path('attempts/<int:id>', views.attempt_detail, name='attempt'),
    path('rejudge/<int:number>', views.rejudge, name='rejudge'),
    path('rejudge_attempt/<int:id>', views.rejudge_attempt, name='rejudge_attempt'),
    path('olympiads', views.contest_list, name='contests'),
    path('olympiads/<int:id>', views.contest_detail, name='contest'),
    path('olympiads/<int:contest_id>/tasks/<str:problem_name>', views.contest_problem, name='contest_problem'),
    path('olympiads/<int:id>/register', views.register_contest, name='register_contest'),
    path('olympiads/<int:id>/attempts', views.contest_submissions, name='contest_attempts'),
    path('olympiads/<int:id>/results', views.contest_results, name='contest_results'),
    path('olympiads/<int:id>/participants', views.contest_participants, name='contest_participants')

]
