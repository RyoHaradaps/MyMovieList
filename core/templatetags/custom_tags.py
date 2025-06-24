from django import template
register = template.Library()

@register.filter
def to(value, arg):
    return range(value, arg + 1)

@register.filter
def equals(val, arg):
    return val == arg

@register.filter
def hours(runtime):
    if runtime is None:
        return ''
    return runtime // 60

@register.filter
def minutes(runtime):
    if runtime is None:
        return ''
    return runtime % 60