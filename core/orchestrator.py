"""
Email Orchestrator - Main Workflow Coordinator
============================================

This module orchestrates the entire cold email automation workflow,
coordinating between data loading, processing, and reporting components.

Author: Cold Email Automation System
Version: 2.0 (Simplified)
"""

import pandas as pd
from typing import Dict, Any
from pipeline import SimpleEmailPipeline
from data.loader import DataLoader
from data.validator import EmailValidator
from processors.preview_processor import PreviewProcessor
from processors.draft_processor import DraftProcessor
from reporting.reporter import ReportGenerator
from utils.logger import setup_logger


class EmailOrchestrator:
    """
    Main orchestrator for the cold email automation system
    
    This class coordinates all the components of the system:
    - Data loading and validation
    - Email processing (preview/draft creation)
    - Reporting and output generation
    """
    
    def __init__(self):
        """Initialize the orchestrator"""
        self.logger = setup_logger('orchestrator')
        self.data_loader = DataLoader()
        self.email_validator = EmailValidator()
        self.preview_processor = PreviewProcessor()
        self.draft_processor = DraftProcessor()
        self.report_generator = ReportGenerator()
    
    def run(self, args):
        """
        Run the requested operation
        
        Args:
            args: Parsed command line arguments
        """
        self.logger.info(f"Starting {args.action} operation")
        
        # Step 1: Load prospect data
        self.logger.info("Step 1: Loading prospect data")
        prospects_df = self.data_loader.load_prospects(args.input, args.limit)
        
        # Step 2: Initialize email pipeline
        self.logger.info("Step 2: Initializing email pipeline")
        pipeline = SimpleEmailPipeline(llm_provider=args.llm)
        
        # Step 3: Execute requested operation
        self.logger.info(f"Step 3: Executing {args.action} operation")
        
        if args.action == 'validate':
            self._handle_validation(prospects_df)
        elif args.action == 'preview':
            self._handle_preview(pipeline, prospects_df)
        elif args.action == 'draft':
            self._handle_draft_creation(pipeline, prospects_df)
        
        self.logger.info(f"{args.action} operation completed successfully")
    
    def _handle_validation(self, prospects_df: pd.DataFrame):
        """Handle email validation operation"""
        validation_results = self.email_validator.validate_emails(prospects_df)
        self.report_generator.display_validation_results(validation_results)
    
    def _handle_preview(self, pipeline: SimpleEmailPipeline, prospects_df: pd.DataFrame):
        """Handle email preview operation"""
        results = self.preview_processor.process_previews(pipeline, prospects_df)
        report = self.report_generator.generate_report(results, len(prospects_df), 'preview')
        self.report_generator.display_summary(report)
        self.report_generator.save_results(results, 'data/email_previews.json', report)
    
    def _handle_draft_creation(self, pipeline: SimpleEmailPipeline, prospects_df: pd.DataFrame):
        """Handle email draft creation operation"""
        results = self.draft_processor.process_drafts(pipeline, prospects_df)
        report = self.report_generator.generate_report(results, len(prospects_df), 'draft')
        self.report_generator.display_summary(report)
        self.report_generator.save_results(results, 'data/draft_results.json', report) 