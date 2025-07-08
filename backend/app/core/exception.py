"""
Custom exceptions for the Iris Data API
"""


class IrisAPIException(Exception):
    """Base exception for Iris API"""
    pass


class DataLoadError(IrisAPIException):
    """Raised when data cannot be loaded"""
    pass


class DataNotFoundError(IrisAPIException):
    """Raised when requested data is not found"""
    pass


class AuthenticationError(IrisAPIException):
    """Raised when authentication fails"""
    pass


class ValidationError(IrisAPIException):
    """Raised when data validation fails"""
    pass


class ConfigurationError(IrisAPIException):
    """Raised when configuration is invalid"""
    pass