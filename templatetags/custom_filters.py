from django import template

register = template.Library()


@register.filter
def splitlines(value):
    """Split text by lines."""
    if value:
        return value.split('\n')
    return []


@register.filter
def get_range(value):
    """Return a range from 1 to value."""
    return range(1, value + 1)
