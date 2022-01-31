from django import template
from django.db.models import Count

register = template.Library()


@register.filter()
def nulls(text, count=4):
    return (count - len(str(text))) * '0' + str(text)


@register.filter()
def millisecond(text):
    return int(text * 1000)


@register.filter()
def accepted_count(qs):
    qs = qs.filter(verdict='Accepted')
    return qs.count()


@register.filter()
def attempts_count(qs):
    return qs.count()


@register.filter()
def users_solved(qs):
    res = qs.filter(verdict='Accepted').values("user").annotate(Count('user__id', distinct=True)).distinct().count()
    return res


@register.filter()
def performance_percentage(qs):
    attempts = attempts_count(qs)
    accepteds = accepted_count(qs)
    if attempts != 0:
        return f'%0.1f' % ((accepteds / attempts) * 100)
    return 0


@register.filter()
def get_penalty(dict):
    attempt = list(dict.values())[0]
    time = list(dict.values())[1]
    if attempt == 0:
        if time == '':
            return ''
        else:
            return '+'
    else:
        if attempt < 0:
            return str(attempt)
        else:
            return f'+{attempt}'


@register.filter()
def get_time(dict):
    return list(dict.values())[1]


@register.filter()
def filter_lang(qs, lang=None):
    return qs.filter(lang=lang).count()