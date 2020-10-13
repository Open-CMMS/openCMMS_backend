"""This file defines extra_tags to use in django html templates."""

from django import template

register = template.Library()


@register.filter(name='extract')
def extract(list, position):
    """Return the element of list 'list' at position 'position'."""
    return list[position]


@register.simple_tag
def def_element(element):
    """Define an object 'element' in a template."""
    return element
