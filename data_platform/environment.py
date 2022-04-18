from enum import Enum


class Environment(Enum):
    """
    Enum for the different environments
    """

    LOCAL = 'local'
    DEV = 'dev'
    STAGING = 'staging'
    PRODUCTION = 'production'
