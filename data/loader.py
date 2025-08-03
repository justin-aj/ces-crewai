"""
Data Loader - Prospect Data Loading Module
=========================================

This module handles loading prospect data from various file formats
(CSV, Excel) and provides data validation and preprocessing.

Author: Cold Email Automation System
Version: 2.0 (Simplified)
"""

import pandas as pd
from typing import Optional
from utils.logger import setup_logger


class DataLoader:
    """
    Data loader for prospect information
    
    Handles loading prospect data from CSV and Excel files,
    with support for data validation and preprocessing.
    """
    
    def __init__(self):
        """Initialize the data loader"""
        self.logger = setup_logger('data_loader')
    
    def load_prospects(self, file_path: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Load prospect data from CSV or Excel file
        
        Args:
            file_path (str): Path to the input file
            limit (int, optional): Maximum number of prospects to process
        
        Returns:
            pd.DataFrame: Loaded prospect data
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
            ValueError: If the file format is not supported
        """
        self.logger.info(f"Loading prospects from {file_path}")
        
        try:
            # Determine file type and load accordingly
            if file_path.endswith('.csv'):
                prospects_df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                prospects_df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            # Apply limit if specified
            if limit:
                prospects_df = prospects_df.head(limit)
                self.logger.info(f"Limited to {limit} prospects")
            
            # Validate required columns
            self._validate_columns(prospects_df)
            
            self.logger.info(f"Successfully loaded {len(prospects_df)} prospects")
            return prospects_df
            
        except FileNotFoundError:
            self.logger.error(f"Input file not found: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading prospect data: {str(e)}")
            raise
    
    def _validate_columns(self, df: pd.DataFrame):
        """
        Validate that required columns are present
        
        Args:
            df (pd.DataFrame): Dataframe to validate
        """
        required_columns = ['name', 'email', 'company', 'role']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        self.logger.info("Column validation passed") 