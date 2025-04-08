from django import template

register = template.Library()


@register.inclusion_tag("parks/display_rating.html")
def render_stars(rating, size):

    # number of whole gold stars
    filled_stars = int(rating)

    decimal = rating - filled_stars

    # half star if 0.25 <= decimal < 0.75
    half_stars = 0
    if 0.25 <= decimal and decimal < 0.75:
        half_stars = 1

    if decimal >= 0.75:
        filled_stars += 1

    empty_stars = 5 - filled_stars - half_stars

    return {
        "filled_stars": filled_stars,
        "half_stars": half_stars,
        "empty_stars": empty_stars,
        "size": size,
    }
