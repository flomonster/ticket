from rolepermissions.permissions import register_object_checker

from core.roles import *
from core.models import *

@register_object_checker()
def add_office(role, user, asso):
    if role == Respo or user.is_superuser:
        return True

    try:
        member = Membership.objects.get(asso=asso, member=user, role__exact=MemberRole.PRESIDENT._value_)
    except:
        return False

    return True

@register_object_checker()
def validate_member(role, user, asso):
    if user.is_superuser:
        return True

    try:
        member = (Membership.objects.filter(asso=asso, role__exact=MemberRole.PRESIDENT._value_) |\
                 Membership.objects.filter(asso=asso, role__exact=MemberRole.OFFICE._value_))\
                 .get(member=user)
    except:
        return False

    return True
