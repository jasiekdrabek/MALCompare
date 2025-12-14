from django import template

register = template.Library()

@register.filter
def get_item(obj, key):
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, "")

@register.filter
def get_status(obj, key):
    if isinstance(obj, dict):
        return obj.get(key, key)
    return getattr(obj, key, "")