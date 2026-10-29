from django import template

register = template.Library()


@register.filter
def fcfa(value):
    """6500 -> '6 500' (espace insécable)."""
    try:
        return f"{int(value):,}".replace(",", "\u00a0")
    except (TypeError, ValueError):
        return value
