from django import template

register = template.Library()


@register.filter
def replace(value, arg):
    old, new = arg.split(",", 1)  # Split only on the first comma
    return value.replace(old, new)
