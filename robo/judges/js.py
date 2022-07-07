import subprocess
import time

from robo.models import Submission, TestCase


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
