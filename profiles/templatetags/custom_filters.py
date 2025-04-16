from django import template

register = template.Library()


@register.filter
def replace(value, args):
    try:
        old, new = args.split(",", 1)
    except ValueError:
        raise ValueError("replace filter expects two arguments separated by a comma")
    return value.replace(old, new)
