"""
Simplified Tools - Import Module
==============================

This module provides imports for all tools from the modular structure.
This maintains backward compatibility while using the new modular organization.

Author: Cold Email Automation System
Version: 2.0 (Simplified)
"""

# Import all tools from their respective modules
from tools.research_tools import CompanyResearchTool
from tools.personalization_tools import ProfileMatcherTool
from tools.writing_tools import EmailWriterTool
from tools.quality_tools import QualityCheckerTool
from tools.sending_tools import GmailSenderTool

# Re-export for backward compatibility
__all__ = [
    'CompanyResearchTool',
    'ProfileMatcherTool',
    'EmailWriterTool', 
    'QualityCheckerTool',
    'GmailSenderTool'
] 