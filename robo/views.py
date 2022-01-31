import time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from colorama import Back
from django.db.models import Q
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import SubmissionForm
from .judges import check_cpp, check_python, check_java, check_js, check_dart, check_pypy, contest_submission
from .models import Problem, Submission, Contest, ContestResult, ContestProblem


def task_list(request):
    start = time.time()
    tasks = Problem.objects.filter(hidden=False).order_by('number')
    accepted_problem_ids = []
    ignored_problem_ids = []
    if request.user.is_authenticated:
        accepted_submissions = Submission.objects.filter(user=request.user, verdict='Accepted').values(
            'problem_id').distinct()
        for submission in accepted_submissions:
            accepted_problem_ids.append(submission['problem_id'])
        ignored_submissions = Submission.objects.filter(~Q(verdict='Accepted'), user=request.user).values(
            'problem_id').distinct()
        for submission in ignored_submissions:
            if not submission['problem_id'] in accepted_problem_ids:
                ignored_problem_ids.append(submission['problem_id'])

    if request.user.is_authenticated and Problem.objects.filter(hidden=True).filter(
            users_can_see=request.user).count() != 0:
        tasks |= Problem.objects.filter(hidden=True).filter(users_can_see=request.user).order_by('number')
    end = time.time()
    return render(request, 'robo/task_list.html', {'tasks': tasks,
                                                   'name': 'tasks',
                                                   'accepted_problem_ids': accepted_problem_ids,
                                                   'ignored_problem_ids': ignored_problem_ids,
                                                   'gen_time': int((end - start) * 1000)})


def task_detail(request, number):
    start = time.time()
    if request.method == 'POST':
        form = SubmissionForm(data=request.POST)
        if form.is_valid():
            problem = Problem.objects.get(number=number)
            submission = form.save(commit=False)
            submission.user = request.user
            submission.problem = problem
            submission.save()
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                'attempt', {
                    'type': 'attempt.message',
                    'created': True,
                    'id': submission.id,
                    'full_name': submission.user.get_full_name(),
                    'username': submission.user.username,
                    'task_name': submission.problem.title,
                    'task_id': submission.problem.id,
                    'lang': submission.lang,
                    'verdict': submission.verdict,
                    'date': str(submission.created)
                })
            print('send')
            cd = form.cleaned_data
            if cd['lang'] == 'cpp':
                check_cpp(submission.id)
            elif cd['lang'] == 'python':
                check_python(submission.id)
            elif cd['lang'] == 'dart':
                check_dart(submission.id)
            elif cd['lang'] == 'java':
                check_java(submission.id)
            elif cd['lang'] == 'js':
                check_js(submission.id)
            elif cd['lang'] == 'pypy':
                check_pypy(submission.id)

    if request.user.is_authenticated:
        task = Problem.objects.get(number=number)
        if task.hidden and request.user not in task.users_can_see.all():
            return HttpResponseNotFound()
    else:
        task = get_object_or_404(Problem, number=number, hidden=False)
    submissions = None
    if request.user.is_authenticated:
        submissions = Submission.objects.filter(problem__number=number, user=request.user).order_by('-id')
    end = time.time()
    return render(request, 'robo/task_detail.html', {'task': task,
                                                     'submissions': submissions,
                                                     'name': 'tasks',
                                                     'gen_time': int((end - start) * 1000)})


def task_attempts(request, number):
    start = time.time()
    submissions = Submission.objects.filter(problem__number=number).order_by('-id')
    end = time.time()
    return render(request, 'robo/task_attempts.html', {'submissions': submissions,
                                                       'taks_number': number,
                                                       'gen_time': int((end - start) * 1000)})


def attempts(request):
    start = time.time()
    submissions = Submission.objects.all().order_by('-id')
    end = time.time()
    return render(request, 'robo/attempts.html', {'submissions': submissions,
                                                  'name': 'attempts',
                                                  'gen_time': int((end - start) * 1000)})


def attempt_detail(request, id):
    start = time.time()
    submission = Submission.objects.get(id=id)
    if submission.user != request.user:
        return redirect('robo:attempts')
    end = time.time()
    return render(request, 'robo/attempts_detail.html', {'submission': submission,
                                                         'name': 'attempts',
                                                         'gen_time': int((end - start) * 1000)})


def rejudge(request, number):
    if request.user.username == 'muhammadjon':
        problem = Problem.objects.get(number=number)
        submissions = Submission.objects.filter(problem_id=problem.id)
        print(f'Rejudge problem {problem.title}')
        print(f'Total submissions {submissions.count()}')
        k = 0
        for submission in submissions:
            k += 1
            print(f'Rejudge submission ({k}/{submissions.count()})')
            if submission.lang == 'cpp':
                if check_cpp(submission.id):
                    print(Back.GREEN + f'Submission {submission.id} {submission.verdict}' + Back.GREEN)
                else:
                    print(Back.RED + f'Submission {submission.id} {submission.verdict}' + Back.RED)
            elif submission.lang == 'python':
                if check_python(submission.id):
                    print(Back.GREEN + f'Submission {submission.id} {submission.verdict}' + Back.GREEN)
                else:
                    print(Back.RED + f'Submission {submission.id} {submission.verdict}' + Back.RED)
        return JsonResponse({'status': 'tugadi'})
    else:
        return JsonResponse({'status': 'manzilda adashdiz!'})


def rejudge_attempt(request, id):
    if request.user.username == 'muhammadjon':
        submission = Submission.objects.get(id=id)
        if submission.lang == 'cpp':
            contest_submission(submission.id)
        elif submission.lang == 'python':
            check_python(submission.id)
        elif submission.lang == 'dart':
            check_dart(submission.id)
        elif submission.lang == 'java':
            check_java(submission.id)
        elif submission.lang == 'js':
            check_js(submission.id)
        elif submission.lang == 'pypy':
            check_pypy(submission.id)
        return JsonResponse({'status': 'tugadi'})
    else:
        return JsonResponse({'status': 'manzilda adashdiz!'})


def contest_list(request):
    start = time.time()
    contests = Contest.objects.all().order_by('-id')
    end = time.time()
    return render(request, 'robo/contest/contest_list.html', {'contests': contests,
                                                              'gen_time': int((end - start) * 1000)})


def contest_detail(request, id):
    start = time.time()
    contest = Contest.objects.get(id=id)
    now = timezone.now()
    host = request.headers['Host']
    end = time.time()
    return render(request, 'robo/contest/contest_detail.html', {'contest': contest,
                                                                'first_problem': 'A',
                                                                'now': now,
                                                                'host': host,
                                                                'name': 'olymp',
                                                                'gen_time': int((end - start) * 1000)})


def register_contest(request, id):
    contest = Contest.objects.get(id=id)
    now = timezone.now()
    if now < contest.start:
        if request.user in contest.participants.all():
            contest.participants.remove(request.user)
        else:
            contest.participants.add(request.user)
    return redirect(contest.get_absolute_url())


def contest_problem(request, contest_id, problem_name):
    start = time.time()
    contest = Contest.objects.get(id=contest_id)
    problem = contest.problems.get(name=problem_name.lower())
    now = timezone.now()

    if contest.start <= now <= contest.end:
        if request.user not in contest.participants.all():
            return HttpResponseNotFound()
    if now < contest.start:
        return HttpResponseNotFound()
    submissions = Submission.objects.filter(problem=problem.problem, contest_id=contest_id,
                                            user_id=request.user.id).order_by('-created')
    if request.method == 'POST':
        form = SubmissionForm(data=request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.problem = problem.problem
            if contest.start <= now <= contest.end:
                submission.contest = contest
            submission.save()
            cd = form.cleaned_data
            if cd['lang'] == 'cpp':
                contest_submission(submission.id)
            elif cd['lang'] == 'python':
                contest_submission(submission.id)
    end = time.time()
    return render(request, 'robo/contest/contest_problem.html', {'contest': contest,
                                                                 'contest_problem': problem,
                                                                 'problem_name': problem_name,
                                                                 'contest_id': contest_id,
                                                                 'submissions': submissions,
                                                                 'first_problem': 'A',
                                                                 'now': now,
                                                                 'name': 'tasks',
                                                                 'gen_time': int((end - start) * 1000)})


def contest_submissions(request, id):
    start = time.time()
    contest = Contest.objects.get(id=id)
    now = timezone.now()
    submissions = Submission.objects.filter(contest_id=id).order_by('-created')
    if contest.start <= now <= contest.end:
        if request.user not in contest.participants.all():
            return HttpResponseNotFound()
    end = time.time()
    return render(request, 'robo/contest/contest_attempts.html', {'contest': contest,
                                                                  'submissions': submissions,
                                                                  'first_problem': 'A',
                                                                  'name': 'attempts',
                                                                  'gen_time': int((end - start) * 1000)})


def contest_results(request, id):
    startt = time.time()
    contest_result = ContestResult.objects.filter(contest_id=id).order_by("-solved_problems_count", 'penalty')
    contest_problem_items = ContestProblem.objects.filter(contest_id=id)
    contest = Contest.objects.get(id=id)
    start = Contest.objects.get(id=id).start
    columns = []
    for items in contest_problem_items:
        columns.append(items.name)
    data = []
    for items in contest_result:
        problems_result = []
        for column in columns:
            solved_time_str = ''
            try:
                solved_time = getattr(items, str(column.upper()) + '_time') - start
                seconds = solved_time.total_seconds()
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                seconds = int(seconds % 60)
                if hours != 0:
                    if hours < 10:
                        solved_time_str += f'0{hours}:'
                    else:
                        solved_time_str += f'{hours}:'
                if minutes < 10:
                    solved_time_str += f'0{minutes}:'
                else:
                    solved_time_str += f'{minutes}:'
                if seconds < 10:
                    solved_time_str += f'0{seconds}'
                else:
                    solved_time_str += f'{seconds}'
            except TypeError:
                pass
            problems_result.append({column: getattr(items, column.upper()),
                                    'time': solved_time_str})
        data.append(
            {
                "user": items.user.get_full_name,
                "username": items.user.username,
                "result": items.solved_problems_count,
                "problems_result": problems_result,
                "penalty": items.penalty
            })
    end = time.time()
    return render(request, 'robo/contest/contest_standings.html', {'contest': contest,
                                                                   'first_problem': 'A',
                                                                   'name': 'standings',
                                                                   'contest_problem_items': contest_problem_items,
                                                                   'data': data,
                                                                   'gen_time': int((end - startt) * 1000)})


def contest_participants(request, id):
    start = time.time()
    contest = Contest.objects.get(id=id)
    users = contest.participants.all()
    end = time.time()
    return render(request, 'robo/contest/contest_participants.html', {'name': 'participants',
                                                                      'first_problem': 'A',
                                                                      'users': users,
                                                                      'contest': contest,
                                                                      'gen_time': int((end - start) * 1000)})
