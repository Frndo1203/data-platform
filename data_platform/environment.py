from enum import Enum


class Environment(Enum):
    """
    Enum for the different environments
    """

    LOCAL = 'local'
    DEVELOP = 'develop'
    STAGING = 'staging'
    PRODUCTION = 'production'
