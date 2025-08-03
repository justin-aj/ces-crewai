"""
Simplified Cold Email Automation System - Main Entry Point
=======================================================

This is the main entry point for the cold email automation system.
It handles command-line argument parsing and orchestrates the workflow.

Author: Cold Email Automation System
Version: 2.0 (Simplified)
"""

import sys
import argparse
from dotenv import load_dotenv
from core.orchestrator import EmailOrchestrator
from utils.logger import setup_logger


def setup_argument_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(
        description='Simplified Cold Email Automation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview emails before sending
  python main.py preview --input prospects.csv --limit 5
  
  # Create email drafts for review
  python main.py draft --input prospects.csv
  
  # Validate email addresses
  python main.py validate --input prospects.csv
        """
    )
    
    # Required arguments
    parser.add_argument('action', 
                       choices=['draft', 'preview', 'validate'],
                       help='Action to perform: draft (create drafts), preview (generate previews), validate (check emails)')
    parser.add_argument('--input', '-i', 
                       required=True,
                       help='Input CSV/Excel file path containing prospect data')
    
    # Optional arguments
    parser.add_argument('--limit', '-l', 
                       type=int, 
                       default=None,
                       help='Limit number of emails to process (useful for testing)')
    parser.add_argument('--llm', 
                       choices=['gemini', 'openai'], 
                       default='gemini',
                       help='LLM provider to use for email generation')
    parser.add_argument('--dry-run', 
                       action='store_true',
                       help='Run without actually sending emails (for preview mode)')
    
    return parser


def main():
    """Main execution function"""
    # Setup argument parser and parse arguments
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv('configs/secrets.env')
    
    # Setup logging
    logger = setup_logger('main')
    logger.info("Cold Email Automation System starting...")
    
    try:
        # Create orchestrator and run the requested operation
        orchestrator = EmailOrchestrator()
        orchestrator.run(args)
        
        logger.info("Cold email automation process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 