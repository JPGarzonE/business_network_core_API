# Constants

# Utils
from enum import Enum

# Enum for entitites visibility
class VisibilityState(Enum):
    PRIVATE = 'PRIVATE'
    OPEN = 'OPEN'
    PERSONALIZED = 'PERSONALIZED'
    DELETED = 'DELETED'