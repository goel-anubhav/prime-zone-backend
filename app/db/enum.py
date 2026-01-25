# Enumeration Class
from enum import Enum

class UserStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    PENDING = 'pending'
    DELETED = 'deleted'

    def __str__(self):
        return self.value
    
class UserType(Enum):
    ADMIN = 'admin'
    BROKER = 'broker'
    BROKER_ALIAS = 'broker_alias'
    AGENT = 'agent'

    def __str__(self):
        return self.value
    
class TokenStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    def __str__(self):
        return self.value

class AuthEvent(Enum):
    REGISTER = 'register'
    LOGIN = 'login'
    LOGOUT = 'logout'
    FORGOT_PASS = 'forgot_pass'
    def __str__(self):
        return self.value