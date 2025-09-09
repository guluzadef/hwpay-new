from django import template

register = template.Library()

@register.filter
def length_is(value, arg):
    """Возвращает True, если длина значения равна аргументу"""
    try:
        return len(value) == int(arg)
    except (ValueError, TypeError):
        return False 