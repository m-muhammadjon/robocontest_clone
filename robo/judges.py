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
