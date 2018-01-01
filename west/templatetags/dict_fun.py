from django import template

register = template.Library()


def dict_get(value, key):
    return dict(value).get(key)


register.filter('dict_get', dict_get)
