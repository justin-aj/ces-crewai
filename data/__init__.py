"""
Data processing module for the Cold Email Automation System
"""

from .loader import DataLoader
from .validator import EmailValidator

__all__ = ['DataLoader', 'EmailValidator'] 