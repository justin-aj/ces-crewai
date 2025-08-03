"""
Preview Processor - Email Preview Generation Module
================================================

This module handles the generation of email previews without
sending or creating drafts, providing a safe way to review
email content before sending.

Author: Cold Email Automation System
Version: 2.0 (Simplified)
"""

import pandas as pd
from typing import List, Dict, Any
from pipeline import SimpleEmailPipeline
from utils.logger import setup_logger


class PreviewProcessor:
    """
    Preview processor for email generation
    
    Handles the generation of email previews for review purposes,
    without actually sending or creating drafts.
    """
    
    def __init__(self):
        """Initialize the preview processor"""
        self.logger = setup_logger('preview_processor')
    
    def process_previews(self, pipeline: SimpleEmailPipeline, prospects_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate email previews without sending or creating drafts
        
        Args:
            pipeline (SimpleEmailPipeline): Initialized email pipeline
            prospects_df (pd.DataFrame): Prospect data to process
        
        Returns:
            list: List of preview results for each prospect
        """
        self.logger.info("Starting email preview generation")
        
        results = []
        
        for idx, row in prospects_df.iterrows():
            prospect_data = row.to_dict()
            self.logger.info(f"Processing prospect {idx + 1}/{len(prospects_df)}: {prospect_data.get('name', 'Unknown')}")
            
            # Generate preview (dry run mode)
            result = pipeline.process_prospect(prospect_data, dry_run=True)
            results.append(result)
            
            # Display preview information
            if result['success']:
                print(f"✓ Generated email for {prospect_data.get('name', 'Unknown')}")
                print(f"  Subject: {result['email']['subject']}")
                print(f"  Template: {result['email']['template_type']}")
            else:
                print(f"✗ Failed to generate email for {prospect_data.get('name', 'Unknown')}: {result.get('error', 'Unknown error')}")
        
        self.logger.info(f"Preview generation complete: {len(results)} prospects processed")
        return results 