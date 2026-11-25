from django import template

register = template.Library()


@register.filter
def get_item(seq, index):
    """Return seq[index] for lists or seq.get(index) for dicts."""
    if seq is None:
        return ""
    if isinstance(seq, dict):
        return seq.get(index, "")
    try:
        return seq[int(index)]
    except (IndexError, KeyError, TypeError, ValueError):
        return ""
