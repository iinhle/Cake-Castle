# orders/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def is_site_owner(user):
    return user.groups.filter(name='SiteOwner').exists()
