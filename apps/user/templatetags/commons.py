from urllib.parse import parse_qs, urlencode

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def append_querystring(context, key, value):
    querystring = context['request'].META['QUERY_STRING']
    parsed = parse_qs(querystring)
    if key in parsed:
        del parsed[key]
    parsed[key] = [value]
    return urlencode(parsed, doseq=True)
