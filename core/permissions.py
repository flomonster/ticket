"""
This module provides function to check permissions for different
actions on the web site.
"""
from rolepermissions.permissions import register_object_checker

from core.roles import *
from core.models import *

@register_object_checker()
def add_office(role, user, asso):
    """
    @brief determine if a user can add a member to the office.
    @param role role of the user.
    @param user user to check.
    @param asso asociation we want to update.
    @return True if user is authorized, False otherwise
    """
    if role == Respo or user.is_superuser:
        return True

    try:
        member = Membership.objects.get(asso=asso, member=user, role__exact=MemberRole.PRESIDENT._value_)
    except:
        return False

    return True

@register_object_checker()
def validate_member(role, user, asso):
    """
    @brief determine if a user can add a member to an association
    @param role role of the user.
    @param user user to check.
    @param asso asociation we want to update.
    @return True if user is authorized, False otherwise
    """
    if user.is_superuser:
        return True

    try:
        member = (Membership.objects.filter(asso=asso, role__exact=MemberRole.PRESIDENT._value_) |\
                 Membership.objects.filter(asso=asso, role__exact=MemberRole.OFFICE._value_))\
                 .get(member=user)
    except:
        return False

    return True

@register_object_checker()
def event_status_change(role, user, event):
    """
    @brief determine if a user can validate or reject an event.
    @param role role of the user.
    @param user user to check.
    @param event event we want to update.
    @return True if user is authorized, False otherwise
    """
    if user.is_superuser or role == Respo:
        return True

    try:
        member = Membership.objects.filter(asso=event.orga, role__exact=MemberRole.PRESIDENT._value_)\
                .get(member=user)
    except:
        return False

    return True
