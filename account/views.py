import time
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.http import HttpResponse
import pathlib
from django.shortcuts import render, redirect

from robo.models import Problem, Submission, Contest
from .forms import UserRegistrationForm, LoginForm
from .models import Profile


def register(request):
    if request.user.is_authenticated:
        return redirect('account:home')
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Profile.objects.create(user=user)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('account:home')
        else:
            return render(request, 'account/register.html', {'errors': form.errors})
    return render(request, 'account/register.html', {'name': 'register'})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('account:home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            print(cd, cd['username'], cd['password'])
            user = authenticate(request, username=cd['username'], password=cd['password'])
            print(user)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('account:home')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    return render(request, 'account/login.html', {'name': 'login'})


def user_logout(request):
    logout(request)
    return redirect('account:home')


def home(request):
    start = time.time()
    print('******', pathlib.Path().resolve())
    users_count = User.objects.all().count()
    submissions_count = Submission.objects.all().count()
    tasks_count = Problem.objects.all().count()
    contests_count = Contest.objects.all().count()
    end = time.time()
    return render(request, 'home.html', {'users_count': users_count,
                                         'submissions_count': submissions_count,
                                         'tasks_count': tasks_count,
                                         'contests_count': contests_count,
                                         'gen_time': int((end - start) * 1000)})


def users(request):
    start = time.time()
    users = User.objects.all()
    end = time.time()
    return render(request, 'account/users.html', {'users': users,
                                                  'name': 'users',
                                                  'gen_time': int((end - start) * 1000)})


def user_profile(request, username):
    start = time.time()
    user = User.objects.get(username=username)
    tasks = Problem.objects.filter(hidden=False).order_by('number')
    accepted_problem_ids = []
    accepted_submissions_set = Submission.objects.filter(user=user, verdict='Accepted').values(
        'problem_id').distinct()
    for submission in accepted_submissions_set:
        accepted_problem_ids.append(submission['problem_id'])
    ignored_problem_ids = []
    ignored_submissions_set = Submission.objects.filter(~Q(verdict='Accepted'), user=user).values(
        'problem_id').distinct()
    for submission in ignored_submissions_set:
        if not submission['problem_id'] in accepted_problem_ids:
            ignored_problem_ids.append(submission['problem_id'])
    tasks_score = list(Problem.objects.all().aggregate(Sum('difficulty')).values())[0]
    solved_score = list(Problem.objects.filter(id__in=accepted_problem_ids).aggregate(Sum('difficulty')).values())[0]
    all_submissions = Submission.objects.filter(user=user)
    accepted_submissions = all_submissions.filter(verdict='Accepted')
    ignored_submissions = all_submissions.filter(~Q(verdict='Accepted'))
    end = time.time()
    return render(request, 'profile/user_profile.html', {'user': user,
                                                         'tasks': tasks,
                                                         'accepted_problem_ids': accepted_problem_ids,
                                                         'ignored_problem_ids': ignored_problem_ids,
                                                         'solved_problem_count': len(accepted_problem_ids),
                                                         'tasks_score': tasks_score,
                                                         'solved_score': solved_score,
                                                         'all_submissions': all_submissions,
                                                         'accepted_submissions': accepted_submissions,
                                                         'ignored_submissions': ignored_submissions,
                                                         'gen_time': int((end - start) * 1000),
                                                         'name': 'profile'})


def user_attempts(request, username):
    start = time.time()
    user = User.objects.get(username=username)
    submissions = Submission.objects.filter(user=user).order_by('-id')
    end = time.time()
    return render(request, 'profile/user_attempts.html', {'submissions': submissions,
                                                          'user': user,
                                                          'name': 'user_attempts',
                                                          'gen_time': int((end - start) * 1000)})


def user_solved_tasks(request, username):
    user = User.objects.get(username=username)
    tasks = Problem.objects.filter(hidden=False)
    return render(request, 'profile/solved_tasks.html', {'user': user,
                                                         'tasks': tasks})
