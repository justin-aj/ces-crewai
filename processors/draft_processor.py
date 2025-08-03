"""
Draft Processor - Email Draft Creation Module
===========================================

This module handles the creation of email drafts in Gmail,
providing a way to review and manually send emails later.

Author: Cold Email Automation System
Version: 2.0 (Simplified)
"""

import pandas as pd
from typing import List, Dict, Any
from pipeline import SimpleEmailPipeline
from utils.logger import setup_logger


class DraftProcessor:
    """
    Draft processor for email creation
    
    Handles the creation of email drafts in Gmail for later
    review and manual sending.
    """
    
    def __init__(self):
        """Initialize the draft processor"""
        self.logger = setup_logger('draft_processor')
    
    def process_drafts(self, pipeline: SimpleEmailPipeline, prospects_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Create email drafts in Gmail for later review and sending
        
        Args:
            pipeline (SimpleEmailPipeline): Initialized email pipeline
            prospects_df (pd.DataFrame): Prospect data to process
        
        Returns:
            list: List of draft creation results for each prospect
        """
        self.logger.info("Starting email draft creation")
        
        results = []
        success_count = 0
        error_count = 0
        
        for idx, row in prospects_df.iterrows():
            prospect_data = row.to_dict()
            self.logger.info(f"Processing prospect {idx + 1}/{len(prospects_df)}: {prospect_data.get('name', 'Unknown')}")
            
            # Create draft
            result = pipeline.process_prospect(prospect_data, create_draft=True)
            results.append(result)
            
            # Display draft creation information
            if result['success']:
                success_count += 1
                print(f"✓ Draft created for {prospect_data.get('name', 'Unknown')}")
                print(f"  Subject: {result['email']['subject']}")
                print(f"  Template: {result['email']['template_type']}")
                if 'draft_id' in result:
                    print(f"  Draft ID: {result['draft_id']}")
            else:
                error_count += 1
                print(f"✗ Failed to create draft for {prospect_data.get('name', 'Unknown')}: {result.get('error', 'Unknown error')}")
        
        self.logger.info(f"Draft creation complete: {success_count} successful, {error_count} failed")
        return results 