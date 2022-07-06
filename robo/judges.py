import datetime
import os
import pathlib
import subprocess
import time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import Submission, TestCase, ContestResult, ContestProblem

os.chdir(str(pathlib.Path().resolve())+'/robo/files')


def check_cpp(id):
    print('C++ checker')
    submission = Submission.objects.get(id=id)
    f = open('program.cpp', 'w+')
    f.write(submission.source)
    f.close()
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        'attempt', {
            'type': 'attempt.message',
            'created': False,
            'id': submission.id,
            'verdict': 'Compiling',
            'tugadi': False
        }
    )
    p1 = subprocess.run('g++ program.cpp -o program.exe',
                        capture_output=True, shell=True)
    if p1.stderr:
        submission.verdict = 'Compilation error'
        submission.errors = str(p1.stderr)
        submission.save()
        async_to_sync(layer.group_send)(
            'attempt', {
                'type': 'attempt.message',
                'created': False,
                'id': submission.id,
                'verdict': 'Compilation error',
                'tugadi': True
            }
        )
        return False
    else:
        k = 0
        tests = TestCase.objects.filter(problem_id=submission.problem.id)
        max_time = 0
        for test in tests:
            k += 1
            input = bytes(test.input, 'UTF-8')
            begin = time.time()
            async_to_sync(layer.group_send)(
                'attempt', {
                    'type': 'attempt.message',
                    'created': False,
                    'id': submission.id,
                    'verdict': f'Running(test {k})',
                    'tugadi': False
                }
            )
            try:
                p2 = subprocess.run('program.exe', input=input, capture_output=True, shell=True,
                                    timeout=submission.problem.time)
                end = time.time()
                max_time = max(max_time, (end - begin) * 1000)
                if p2.stderr:
                    submission.verdict = f'Runtime error (test {k})'
                    submission.time = max_time
                    submission.save()
                    async_to_sync(layer.group_send)(
                        'attempt', {
                            'type': 'attempt.message',
                            'created': False,
                            'id': submission.id,
                            'verdict': f'Runtime error (test {k})',
                            'tugadi': True,
                            'time': submission.time
                        }
                    )
                    return False
                else:
                    if p2.stdout.decode('UTF-8').strip() != test.output:
                        submission.verdict = f'Wrong answer (test {k})'
                        submission.time = max_time
                        submission.save()
                        async_to_sync(layer.group_send)(
                            'attempt', {
                                'type': 'attempt.message',
                                'created': False,
                                'id': submission.id,
                                'verdict': f'Wrong answer (test {k})',
                                'tugadi': True,
                                'time': submission.time
                            }
                        )
                        return False
                    else:
                        pass
                        # print(f'Test {k} running {int((end - begin) * 1000)}ms')

            except subprocess.TimeoutExpired:
                end = time.time()
                max_time = max(max_time, (end - begin) * 1000)
                # print(f'Time limit Test {k}')
                submission.verdict = f'Time limit (test {k})'
                submission.time = max_time
                submission.save()
                async_to_sync(layer.group_send)(
                    'attempt', {
                        'type': 'attempt.message',
                        'created': False,
                        'id': submission.id,
                        'verdict': f'Time limit (test {k})',
                        'tugadi': True,
                        'time': submission.time
                    }
                )
                return False
        submission.verdict = 'Accepted'
        submission.time = max_time
        submission.save()
        async_to_sync(layer.group_send)(
            'attempt', {
                'type': 'attempt.message',
                'created': False,
                'id': submission.id,
                'verdict': f'Accepted',
                'tugadi': True,
                'time': submission.time
            }
        )
        return True


def check_python(id):
    print('Python checker')
    submission = Submission.objects.get(id=id)
    f = open('program.py', 'w+')
    f.write(submission.source)
    f.close()
    k = 0
    tests = TestCase.objects.filter(problem_id=submission.problem.id)
    max_time = 0
    for test in tests:
        k += 1
        input = bytes(test.input, 'UTF-8')
        begin = time.time()
        try:
            p = subprocess.run('python program.py', input=input, capture_output=True, shell=False,
                               check=True,
                               timeout=submission.problem.time)
            end = time.time()
            max_time = max(max_time, (end - begin) * 1000)
            if p.stdout.decode('UTF-8').strip() != test.output:
                submission.verdict = f'Wrong answer (test {k})'
                submission.time = max_time
                submission.save()
                return False
            else:
                # print(f'Test {k} running {int((end - begin) * 1000)}ms')
                pass

        except subprocess.TimeoutExpired:
            end = time.time()
            max_time = max(max_time, (end - begin) * 1000)
            # print(f'Time limit Test {k}')
            submission.verdict = f'Time limit (test {k})'
            submission.time = max_time
            submission.save()
            return False
        except subprocess.CalledProcessError as err:
            end = time.time()
            max_time = max(max_time, (end - begin) * 1000)
            if 'SyntaxError' in err.stderr.decode('UTF-8'):
                submission.verdict = f'Compilation error'
                submission.errors = str(err.stderr)
                submission.save()
                return False
            else:
                submission.verdict = f'Runtime error (test {k})'
                submission.time = max_time
                submission.save()
                return False

    submission.verdict = 'Accepted'
    submission.time = max_time
    submission.save()
    return True


def check_pypy(id):
    print('PyPy checker')
    submission = Submission.objects.get(id=id)
    f = open('program.py', 'w+')
    f.write(submission.source)
    f.close()
    k = 0
    tests = TestCase.objects.filter(problem_id=submission.problem.id)
    max_time = 0
    for test in tests:
        k += 1
        input = bytes(test.input, 'UTF-8')
        begin = time.time()
        try:
            p = subprocess.run('pypy3 program.py', input=input, capture_output=True, shell=False,
                               check=True,
                               timeout=submission.problem.time)
            end = time.time()
            max_time = max(max_time, (end - begin) * 1000)
            if p.stdout.decode('UTF-8').strip() != test.output:
                submission.verdict = f'Wrong answer (test {k})'
                submission.time = max_time
                submission.save()
                return False
            else:
                # print(f'Test {k} running {int((end - begin) * 1000)}ms')
                pass

        except subprocess.TimeoutExpired:
            end = time.time()
            max_time = max(max_time, (end - begin) * 1000)
            # print(f'Time limit Test {k}')
            submission.verdict = f'Time limit (test {k})'
            submission.time = max_time
            submission.save()
            return False
        except subprocess.CalledProcessError as err:
            end = time.time()
            max_time = max(max_time, (end - begin) * 1000)
            if 'SyntaxError' in err.stderr.decode('UTF-8'):
                submission.verdict = f'Compilation error'
                submission.errors = str(err.stderr)
                submission.save()
                return False
            else:
                submission.verdict = f'Runtime error (test {k})'
                submission.time = max_time
                submission.save()
                return False

    submission.verdict = 'Accepted'
    submission.time = max_time
    submission.save()
    return True


def check_java(id):
    print('Java checker')
    submission = Submission.objects.get(id=id)
    f = open('Main.java', 'w+')
    f.write(submission.source)
    f.close()
    p1 = subprocess.run('javac Main.java',
                        capture_output=True, text=True, shell=True)
    if p1.stderr:
        print(p1.stderr)
        submission.verdict = 'Compilation error'
        submission.errors = str(p1.stderr)
        submission.save()
        return False
    else:
        k = 0
        tests = TestCase.objects.filter(problem_id=submission.problem.id)
        max_time = 0
        for test in tests:
            k += 1
            input = bytes(test.input, 'UTF-8')
            begin = time.time()
            try:
                p2 = subprocess.run('java Main', input=input, capture_output=True, shell=True,
                                    timeout=submission.problem.time, check=True)
                end = time.time()
                max_time = max(max_time, (end - begin) * 1000)
                if p2.stdout.decode('UTF-8').strip() != test.output:
                    submission.verdict = f'Wrong answer (test {k})'
                    submission.time = max_time
                    submission.save()
                    return False
                else:
                    print(f'Test {k} running {int((end - begin) * 1000)}ms')
                    # pass

            except subprocess.TimeoutExpired:
                end = time.time()
                max_time = max(max_time, (end - begin) * 1000)
                # print(f'Time limit Test {k}')
                submission.verdict = f'Time limit (test {k})'
                submission.time = max_time
                submission.save()
                return False
            except subprocess.CalledProcessError as exc:
                print(exc.stderr.decode('UTF-8'))
                end = time.time()
                max_time = max(max_time, (end - begin) * 1000)
                submission.verdict = f'Runtime error (test {k})'
                submission.time = max_time
                submission.save()
                return False

    submission.verdict = 'Accepted'
    submission.time = max_time
    submission.save()
    return True


def check_js(id):
    print('NodeJs checker')
    submission = Submission.objects.get(id=id)
    f = open('app.js', 'w+')
    f.write(submission.source)
    f.close()
    k = 0
    tests = TestCase.objects.filter(problem_id=submission.problem.id)
    max_time = 0
    for test in tests:
        k += 1
        input = bytes(test.input, 'UTF-8')
        begin = time.time()
        try:
            p = subprocess.run('node app.js', input=input, capture_output=True, shell=False,
                               check=True,
                               timeout=submission.problem.time)
            end = time.time()
            max_time = max(max_time, (end - begin) * 1000)
            if p.stdout.decode('UTF-8').strip() != test.output:
                submission.verdict = f'Wrong answer (test {k})'
                submission.time = max_time
                submission.save()
                return False
            else:
                # print(f'Test {k} running {int((end - begin) * 1000)}ms')
                pass

        except subprocess.TimeoutExpired:
            end = time.time()
            max_time = max(max_time, (end - begin) * 1000)
            # print(f'Time limit Test {k}')
            submission.verdict = f'Time limit (test {k})'
            submission.time = max_time
            submission.save()
            return False
        except subprocess.CalledProcessError as err:
            end = time.time()
            max_time = max(max_time, (end - begin) * 1000)
            submission.verdict = f'Runtime error (test {k})'
            submission.time = max_time
            submission.save()
            return False

    submission.verdict = 'Accepted'
    submission.time = max_time
    submission.save()
    return True


def check_dart(id):
    print('Dart checker')
    submission = Submission.objects.get(id=id)
    f = open('program.dart', 'w+')
    f.write(submission.source)
    f.close()
    p1 = subprocess.run('dart compile exe program.dart -o program.exe',
                        capture_output=True, shell=True)
    if p1.stderr:
        print(p1.stderr.decode('UTF-8'))
        submission.verdict = 'Compilation error'
        submission.errors = str(p1.stderr.decode('UTF-8'))
        submission.save()
        return False
    else:
        k = 0
        tests = TestCase.objects.filter(problem_id=submission.problem.id)
        max_time = 0
        for test in tests:
            k += 1
            input = bytes(test.input, 'UTF-8')
            begin = time.time()
            try:
                p2 = subprocess.run('program.exe', input=input, capture_output=True, shell=True,
                                    timeout=submission.problem.time, check=True)
                end = time.time()
                max_time = max(max_time, (end - begin) * 1000)
                if p2.stdout.decode('UTF-8').strip() != test.output:
                    submission.verdict = f'Wrong answer (test {k})'
                    submission.time = max_time
                    submission.save()
                    return False
                else:
                    pass
                    # print(f'Test {k} running {int((end - begin) * 1000)}ms')

            except subprocess.TimeoutExpired:
                end = time.time()
                max_time = max(max_time, (end - begin) * 1000)
                # print(f'Time limit Test {k}')
                submission.verdict = f'Time limit (test {k})'
                submission.time = max_time
                submission.save()
                return False
            except subprocess.CalledProcessError as err:
                end = time.time()
                print(err.stderr.decode('UTF-8'))
                max_time = max(max_time, (end - begin) * 1000)
                submission.verdict = f'Runtime error (test {k})'
                submission.time = max_time
                submission.save()
                return False

    submission.verdict = 'Accepted'
    submission.time = max_time
    submission.save()
    return True


def contest_submission(id):
    now = timezone.now()
    dt = datetime.datetime.now()
    submission = Submission.objects.get(id=id)
    contest = submission.contest
    contest_result, created = ContestResult.objects.get_or_create(contest=contest, user_id=submission.user_id)
    contest_problem = ContestProblem.objects.get(contest=contest, problem=submission.problem)
    # print('>>>', contest_problem)
    # print('>>>', contest_problem.name)
    # print('>>>', contest_result)
    if submission.lang == 'cpp':
        if check_cpp(submission.id):
            code = f"""if contest_result.{contest_problem.name.upper()}_time is None:
    contest_result.{contest_problem.name.upper()} = abs(contest_result.{contest_problem.name.upper()})
    contest_result.{contest_problem.name.upper()}_time = datetime.datetime.now()
    contest_result.solved_problems_count +=1
    contest_result.penalty += (abs(contest_result.{contest_problem.name.upper()})*5+int((now-contest.start).total_seconds()//60))
    contest_result.save()"""
            exec(code)
        else:
            code = f"""if contest_result.{contest_problem.name.upper()}_time is None:
    contest_result.{contest_problem.name.upper()} -= 1
    contest_result.save()"""
            exec(code)
