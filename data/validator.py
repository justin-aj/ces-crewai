"""
Email Validator - Email Address Validation Module
===============================================

This module handles email address validation for prospect data,
providing comprehensive validation and reporting capabilities.

Author: Cold Email Automation System
Version: 2.0 (Simplified)
"""

import pandas as pd
from typing import Dict, Any
from utils.validators import validate_email_list
from utils.logger import setup_logger


class EmailValidator:
    """
    Email validator for prospect data
    
    Handles email address validation and provides detailed
    reporting on validation results.
    """
    
    def __init__(self):
        """Initialize the email validator"""
        self.logger = setup_logger('email_validator')
    
    def validate_emails(self, prospects_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate email addresses in the prospect data
        
        Args:
            prospects_df (pd.DataFrame): Prospect data containing email column
        
        Returns:
            dict: Validation results with valid/invalid email counts
        """
        self.logger.info("Starting email validation process")
        
        # Extract email addresses
        email_list = prospects_df['email'].tolist()
        
        # Validate emails
        valid_emails = validate_email_list(email_list)
        invalid_emails = set(email_list) - set(valid_emails)
        
        # Prepare results
        validation_results = {
            'total_emails': len(email_list),
            'valid_emails': len(valid_emails),
            'invalid_emails': len(invalid_emails),
            'valid_email_list': list(valid_emails),
            'invalid_email_list': list(invalid_emails),
            'success_rate': len(valid_emails) / len(email_list) * 100
        }
        
        self.logger.info(f"Validation complete: {validation_results['valid_emails']}/{validation_results['total_emails']} emails valid")
        return validation_results 