from rolepermissions.roles import AbstractUserRole

class Respo(AbstractUserRole):
    available_permissions = {
            'designate_pres': True,
    }