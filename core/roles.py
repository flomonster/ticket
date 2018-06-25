"""
This module defines roles of users.
"""
from rolepermissions.roles import AbstractUserRole

class Respo(AbstractUserRole):
    """
    Class to represent the association manager and his permissions.
    """
    available_permissions = {
            'designate_pres': True,
            'make_premium': True,
            'manage': True
    }
