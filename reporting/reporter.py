"""
Report Generator - Reporting and Output Module
===========================================

This module handles the generation of reports, summaries, and
output files for the cold email automation system.

Author: Cold Email Automation System
Version: 2.0 (Simplified)
"""

import os
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from utils.logger import setup_logger


class ReportGenerator:
    """
    Report generator for processing results
    
    Handles the generation of reports, summaries, and output
    files for various operations.
    """
    
    def __init__(self):
        """Initialize the report generator"""
        self.logger = setup_logger('report_generator')
    
    def generate_report(self, results: List[Dict[str, Any]], total_prospects: int, operation_type: str) -> Dict[str, Any]:
        """
        Generate a comprehensive processing report
        
        Args:
            results (list): Processing results for all prospects
            total_prospects (int): Total number of prospects processed
            operation_type (str): Type of operation (preview/draft)
        
        Returns:
            dict: Processing report with statistics
        """
        success_count = sum(1 for r in results if r.get('success', False))
        error_count = total_prospects - success_count
        success_rate = (success_count / total_prospects * 100) if total_prospects > 0 else 0
        
        report = {
            'operation_type': operation_type,
            'total_prospects': total_prospects,
            'successful': success_count,
            'failed': error_count,
            'success_rate': success_rate,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        return report
    
    def display_summary(self, report: Dict[str, Any]):
        """
        Display a formatted processing summary
        
        Args:
            report (dict): Processing report to display
        """
        print(f"\n{'='*50}")
        print(f"PROCESSING SUMMARY")
        print(f"{'='*50}")
        print(f"Operation: {report['operation_type'].title()}")
        print(f"Total Prospects: {report['total_prospects']}")
        print(f"Successful: {report['successful']}")
        print(f"Failed: {report['failed']}")
        print(f"Success Rate: {report['success_rate']:.1f}%")
        print(f"Timestamp: {report['timestamp']}")
        print(f"{'='*50}")
    
    def display_validation_results(self, validation_results: Dict[str, Any]):
        """
        Display email validation results
        
        Args:
            validation_results (dict): Validation results to display
        """
        print(f"\nEmail Validation Results:")
        print(f"Valid emails: {validation_results['valid_emails']}/{validation_results['total_emails']}")
        print(f"Success rate: {validation_results['success_rate']:.1f}%")
        
        if validation_results['invalid_email_list']:
            print(f"Invalid emails: {validation_results['invalid_email_list']}")
    
    def save_results(self, results: List[Dict[str, Any]], file_path: str, report: Optional[Dict[str, Any]] = None):
        """
        Save processing results to JSON file
        
        Args:
            results (list): Processing results to save
            file_path (str): Path to save the results file
            report (dict, optional): Processing report to include
        """
        self.logger.info(f"Saving results to {file_path}")
        
        # Prepare data for saving
        output_data = {
            'results': results,
            'summary': report
        }
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            
            self.logger.info(f"Results saved to {file_path}")
            print(f"Results saved to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
            print(f"Error saving results: {str(e)}") 