import subprocess
import time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from robo.models import Submission, TestCase


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
                p2 = subprocess.run('./program.exe', input=input, capture_output=True, shell=True,
                                    timeout=submission.problem.time)
                end = time.time()
                max_time = max(max_time, (end - begin) * 1000)
                if p2.stderr:
                    submission.verdict = f'Runtime error (test {k})'
                    print(p2.stderr)
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
