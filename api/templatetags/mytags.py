from django import template
register = template.Library()

@register.filter
def split_id(data):
    print(data)
    if data:
        return data.split('#')[0]
    else:
        return ''

