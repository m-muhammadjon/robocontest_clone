import os
import pathlib
import subprocess
import time

from robo.models import Submission, TestCase

os.chdir(str(pathlib.Path().resolve()) + '/robo/files')


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
