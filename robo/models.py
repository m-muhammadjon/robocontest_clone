from string import ascii_lowercase

from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.urls import reverse


class ProgrammingLanguage(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Problem(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.SET_NULL,
                               related_name='problems',
                               null=True)
    number = models.PositiveSmallIntegerField(unique=True)
    title = models.CharField(max_length=255)
    body = RichTextField()
    input = RichTextField()
    output = RichTextField()
    type = models.CharField(max_length=255, null=True, blank=True)
    memory = models.PositiveSmallIntegerField()
    time = models.FloatField()
    difficulty = models.PositiveSmallIntegerField(default=0)
    hidden = models.BooleanField(default=False)
    users_can_see = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('robo:task', args=[self.number])


class Sample(models.Model):
    problem = models.ForeignKey(Problem,
                                on_delete=models.CASCADE,
                                related_name='samples')
    input = models.TextField()
    output = models.TextField()


class TestCase(models.Model):
    problem = models.ForeignKey(Problem,
                                on_delete=models.CASCADE,
                                related_name='tests')
    input = models.TextField()
    output = models.TextField()


class Submission(models.Model):
    LANGUAGE_CHOICES = (
        ('cpp', 'C++'),
        ('python', 'Python'),
        ('java', 'Java'),
        ('dart', 'Dart'),
        ('js', 'Js'),
        ('pypy', 'PyPy')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='submissions')
    problem = models.ForeignKey(Problem,
                                on_delete=models.CASCADE,
                                related_name='submissions')
    lang = models.CharField(choices=LANGUAGE_CHOICES, max_length=20)
    source = models.TextField()
    time = models.PositiveIntegerField(default=0)
    memory = models.PositiveIntegerField(default=0)
    errors = models.TextField(null=True, blank=True)
    verdict = models.CharField(max_length=255, default='Waiting')
    created = models.DateTimeField(auto_now_add=True)
    contest = models.ForeignKey("Contest",
                                related_name='submissions',
                                on_delete=models.CASCADE,
                                null=True, blank=True)


class Contest(models.Model):
    STATUS_CHOICES = (
        ('boshlanmagan', 'Boshlanmagan'),
        ('otkazilmoqda', 'O\'tkazilmoqda'),
        ('tugagan', 'Tugagan')
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='boshlanmagan')
    start = models.DateTimeField()
    end = models.DateTimeField()
    langs = models.ManyToManyField(ProgrammingLanguage)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                          related_name='participated_contests',
                                          null=True, blank=True)

    def __str__(self):
        return self.name

    def get_duration(self):
        return self.end - self.start

    def get_absolute_url(self):
        return reverse('robo:contest', args=[self.id])


class ContestProblem(models.Model):
    a = []
    for i in ascii_lowercase:
        a.append((i, i.upper()))
    NAME_CHOICES = tuple(a)
    contest = models.ForeignKey(Contest,
                                related_name='problems',
                                on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem,
                                on_delete=models.CASCADE)
    name = models.CharField(max_length=10, choices=NAME_CHOICES, null=True)

    def __str__(self):
        return f'Problem for {self.contest.name}'

    def get_absolute_url(self):
        return reverse('robo:contest_problem', args=[self.contest.id,
                                                     self.name.upper()])


class ContestResult(models.Model):
    contest = models.ForeignKey(Contest,
                                related_name='results',
                                on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='contest_results',
                             on_delete=models.CASCADE)
    A = models.SmallIntegerField(default=0)
    B = models.SmallIntegerField(default=0)
    C = models.SmallIntegerField(default=0)
    D = models.SmallIntegerField(default=0)
    E = models.SmallIntegerField(default=0)
    F = models.SmallIntegerField(default=0)
    G = models.SmallIntegerField(default=0)
    H = models.SmallIntegerField(default=0)
    I = models.SmallIntegerField(default=0)
    J = models.SmallIntegerField(default=0)
    K = models.SmallIntegerField(default=0)
    L = models.SmallIntegerField(default=0)
    M = models.SmallIntegerField(default=0)
    N = models.SmallIntegerField(default=0)
    O = models.SmallIntegerField(default=0)
    P = models.SmallIntegerField(default=0)
    Q = models.SmallIntegerField(default=0)
    R = models.SmallIntegerField(default=0)
    S = models.SmallIntegerField(default=0)
    T = models.SmallIntegerField(default=0)
    U = models.SmallIntegerField(default=0)
    V = models.SmallIntegerField(default=0)
    W = models.SmallIntegerField(default=0)
    X = models.SmallIntegerField(default=0)
    Y = models.SmallIntegerField(default=0)
    Z = models.SmallIntegerField(default=0)

    A_time = models.DateTimeField(null=True, blank=True)
    B_time = models.DateTimeField(null=True, blank=True)
    C_time = models.DateTimeField(null=True, blank=True)
    D_time = models.DateTimeField(null=True, blank=True)
    E_time = models.DateTimeField(null=True, blank=True)
    F_time = models.DateTimeField(null=True, blank=True)
    G_time = models.DateTimeField(null=True, blank=True)
    H_time = models.DateTimeField(null=True, blank=True)
    I_time = models.DateTimeField(null=True, blank=True)
    J_time = models.DateTimeField(null=True, blank=True)
    K_time = models.DateTimeField(null=True, blank=True)
    L_time = models.DateTimeField(null=True, blank=True)
    M_time = models.DateTimeField(null=True, blank=True)
    N_time = models.DateTimeField(null=True, blank=True)
    O_time = models.DateTimeField(null=True, blank=True)
    P_time = models.DateTimeField(null=True, blank=True)
    Q_time = models.DateTimeField(null=True, blank=True)
    R_time = models.DateTimeField(null=True, blank=True)
    S_time = models.DateTimeField(null=True, blank=True)
    T_time = models.DateTimeField(null=True, blank=True)
    U_time = models.DateTimeField(null=True, blank=True)
    V_time = models.DateTimeField(null=True, blank=True)
    W_time = models.DateTimeField(null=True, blank=True)
    X_time = models.DateTimeField(null=True, blank=True)
    Y_time = models.DateTimeField(null=True, blank=True)
    Z_time = models.DateTimeField(null=True, blank=True)

    solved_problems_count = models.PositiveSmallIntegerField(default=0)
    ball = models.PositiveSmallIntegerField(default=0)
    penalty = models.PositiveIntegerField(default=0)
