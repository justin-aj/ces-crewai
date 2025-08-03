"""
Simplified Email Pipeline for Cold Email Automation
=================================================

This module contains the core email processing pipeline that orchestrates
the entire cold email automation workflow. It manages the flow between
different processing phases and coordinates the various AI agents and tools.

Pipeline Phases:
1. Research - Gather company information
2. Personalization - Match user profile with job requirements
3. Email Writing - Generate personalized email content
4. Quality Check - Review and improve email quality
5. Draft Creation - Create email drafts in Gmail

Key Components:
- SimpleEmailPipeline: Main pipeline orchestrator
- Agent Management: Creates and manages CrewAI agents
- Phase Processing: Handles each processing phase
- Result Management: Creates standardized result objects

Author: Cold Email Automation System
Version: 2.0 (Simplified)
"""

from crewai import Agent, Task, Crew
from typing import Dict, Any, List
from tools.research_tools import CompanyResearchTool
from tools.personalization_tools import ProfileMatcherTool
from tools.writing_tools import EmailWriterTool
from tools.quality_tools import QualityCheckerTool
from tools.sending_tools import GmailSenderTool
from utils.logger import setup_logger
import json
import time
import yaml


# =============================================================================
# PIPELINE CONFIGURATION
# =============================================================================

class PipelineConfig:
    """Configuration class for pipeline settings and constants"""
    
    # Agent configuration file path
    AGENT_CONFIG_PATH = 'configs/agent_config.yaml'
    
    # Default LLM provider
    DEFAULT_LLM_PROVIDER = 'gemini'
    
    # Processing phases
    PHASES = ['research', 'personalization', 'writing', 'quality', 'draft_creation']
    
    # Result status codes
    STATUS_SUCCESS = 'success'
    STATUS_ERROR = 'error'


# =============================================================================
# AGENT MANAGEMENT
# =============================================================================

class AgentManager:
    """Manages the creation and configuration of CrewAI agents"""
    
    def __init__(self, tools: Dict[str, Any]):
        """
        Initialize agent manager with tools
        
        Args:
            tools (Dict[str, Any]): Dictionary of available tools
        """
        self.tools = tools
        self.logger = setup_logger('agent_manager')
        self.agent_configs = self._load_agent_configs()
    
    def _load_agent_configs(self) -> Dict[str, Any]:
        """
        Load agent configurations from YAML file
        
        Returns:
            Dict[str, Any]: Agent configuration data
        """
        try:
            with open(PipelineConfig.AGENT_CONFIG_PATH, 'r') as f:
                configs = yaml.safe_load(f)
            self.logger.info("Agent configurations loaded successfully")
            return configs
        except Exception as e:
            self.logger.error(f"Error loading agent configs: {str(e)}")
            raise
    
    def create_researcher_agent(self) -> Agent:
        """Create the researcher agent for company analysis"""
        config = self.agent_configs['researcher']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[self.tools['research'].research_company],
            verbose=True
        )
    
    def create_personalizer_agent(self) -> Agent:
        """Create the personalizer agent for profile matching"""
        config = self.agent_configs['personalizer']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[self.tools['personalizer'].match_profile],
            verbose=True
        )
    
    def create_writer_agent(self) -> Agent:
        """Create the email writer agent for content generation"""
        config = self.agent_configs['email_writer']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[self.tools['writer'].write_email],
            verbose=True
        )
    
    def create_quality_checker_agent(self) -> Agent:
        """Create the quality checker agent for email review"""
        config = self.agent_configs['quality_checker']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[self.tools['checker'].check_email_quality],
            verbose=True
        )
    
    def create_draft_creator_agent(self) -> Agent:
        """Create the draft creator agent for Gmail draft creation"""
        return Agent(
            role="Email Draft Creator",
            goal="Create email drafts in Gmail for later review and sending",
            backstory="You are an expert at creating professional email drafts that are ready for human review and approval before sending.",
            tools=[self.tools['sender'].create_draft],
            verbose=True
        )
    
    def create_all_agents(self) -> Dict[str, Agent]:
        """
        Create all agents for the pipeline
        
        Returns:
            Dict[str, Agent]: Dictionary of all created agents
        """
        self.logger.info("Creating all pipeline agents")
        
        agents = {
            'researcher': self.create_researcher_agent(),
            'personalizer': self.create_personalizer_agent(),
            'writer': self.create_writer_agent(),
            'checker': self.create_quality_checker_agent(),
            'draft_creator': self.create_draft_creator_agent()
        }
        
        self.logger.info(f"Created {len(agents)} agents successfully")
        return agents


# =============================================================================
# TOOL MANAGEMENT
# =============================================================================

class ToolManager:
    """Manages the initialization and organization of pipeline tools"""
    
    def __init__(self):
        """Initialize tool manager and create all tools"""
        self.logger = setup_logger('tool_manager')
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """
        Initialize all tools used by the pipeline
        
        Returns:
            Dict[str, Any]: Dictionary of initialized tools
        """
        self.logger.info("Initializing pipeline tools")
        
        tools = {
            'research': CompanyResearchTool(),
            'personalizer': ProfileMatcherTool(),
            'writer': EmailWriterTool(),
            'checker': QualityCheckerTool(),
            'sender': GmailSenderTool()
        }
        
        self.logger.info(f"Initialized {len(tools)} tools successfully")
        return tools
    
    def get_tools(self) -> Dict[str, Any]:
        """Get all initialized tools"""
        return self.tools


# =============================================================================
# PHASE PROCESSING
# =============================================================================

class PhaseProcessor:
    """Handles the processing of individual pipeline phases"""
    
    def __init__(self, tools: Dict[str, Any]):
        """
        Initialize phase processor with tools
        
        Args:
            tools (Dict[str, Any]): Dictionary of available tools
        """
        self.tools = tools
        self.logger = setup_logger('phase_processor')
    
    def process_research_phase(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the research phase - gather company information
        
        Args:
            prospect_data (Dict[str, Any]): Prospect information
            
        Returns:
            Dict[str, Any]: Research phase result with success/error status
        """
        self.logger.info(f"Starting research phase for {prospect_data.get('name', 'Unknown')}")
        
        try:
            company_name = prospect_data.get('company', 'Unknown Company')
            research_data = self.tools['research'].research_company(company_name)
            
            result = {
                'success': True,
                'data': research_data,
                'phase': 'research',
                'company_name': company_name
            }
            
            self.logger.info(f"Research phase completed successfully for {company_name}")
            return result
            
        except Exception as e:
            error_msg = f"Research failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'phase': 'research'
            }
    
    def process_personalization_phase(self, prospect_data: Dict[str, Any], 
                                    research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the personalization phase - match profile with job
        
        Args:
            prospect_data (Dict[str, Any]): Prospect information
            research_data (Dict[str, Any]): Research data from previous phase
            
        Returns:
            Dict[str, Any]: Personalization phase result
        """
        self.logger.info(f"Starting personalization phase for {prospect_data.get('name', 'Unknown')}")
        
        try:
            matches = self.tools['personalizer'].match_profile(prospect_data, research_data)
            
            result = {
                'success': True,
                'data': matches,
                'phase': 'personalization',
                'prospect_name': prospect_data.get('name', 'Unknown')
            }
            
            self.logger.info(f"Personalization phase completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Personalization failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'phase': 'personalization'
            }
    
    def process_writing_phase(self, prospect_data: Dict[str, Any], 
                            research_data: Dict[str, Any], 
                            personalization_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the writing phase - generate email content
        
        Args:
            prospect_data (Dict[str, Any]): Prospect information
            research_data (Dict[str, Any]): Research data
            personalization_data (Dict[str, Any]): Personalization data
            
        Returns:
            Dict[str, Any]: Writing phase result
        """
        self.logger.info(f"Starting writing phase for {prospect_data.get('name', 'Unknown')}")
        
        try:
            email_data = self.tools['writer'].write_email(prospect_data, research_data, personalization_data)
            
            result = {
                'success': True,
                'data': email_data,
                'phase': 'writing',
                'prospect_name': prospect_data.get('name', 'Unknown')
            }
            
            self.logger.info(f"Writing phase completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Writing failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'phase': 'writing'
            }
    
    def process_quality_phase(self, prospect_data: Dict[str, Any], 
                            email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the quality check phase - review and improve email
        
        Args:
            prospect_data (Dict[str, Any]): Prospect information
            email_data (Dict[str, Any]): Email data from writing phase
            
        Returns:
            Dict[str, Any]: Quality check phase result
        """
        self.logger.info(f"Starting quality check phase for {prospect_data.get('name', 'Unknown')}")
        
        try:
            improved_email = self.tools['checker'].check_email_quality(prospect_data, email_data)
            
            result = {
                'success': True,
                'data': improved_email,
                'phase': 'quality',
                'prospect_name': prospect_data.get('name', 'Unknown')
            }
            
            self.logger.info(f"Quality check phase completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Quality check failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'phase': 'quality'
            }
    
    def process_draft_creation_phase(self, prospect_data: Dict[str, Any], 
                                   email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the draft creation phase - create email draft in Gmail
        
        Args:
            prospect_data (Dict[str, Any]): Prospect information
            email_data (Dict[str, Any]): Email data from quality phase
            
        Returns:
            Dict[str, Any]: Draft creation phase result
        """
        self.logger.info(f"Starting draft creation phase for {prospect_data.get('name', 'Unknown')}")
        
        try:
            draft_result = self.tools['sender'].create_draft(prospect_data, email_data)
            
            result = {
                'success': True,
                'data': draft_result,
                'phase': 'draft_creation',
                'prospect_name': prospect_data.get('name', 'Unknown')
            }
            
            self.logger.info(f"Draft creation phase completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Draft creation failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'phase': 'draft_creation'
            }


# =============================================================================
# RESULT MANAGEMENT
# =============================================================================

class ResultManager:
    """Manages the creation and formatting of pipeline results"""
    
    def __init__(self):
        """Initialize result manager"""
        self.logger = setup_logger('result_manager')
    
    def create_success_result(self, prospect_data: Dict[str, Any], 
                            email_data: Dict[str, Any], 
                            draft_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a success result object
        
        Args:
            prospect_data (Dict[str, Any]): Original prospect data
            email_data (Dict[str, Any]): Generated email data
            draft_result (Dict[str, Any], optional): Draft creation result
            
        Returns:
            Dict[str, Any]: Formatted success result
        """
        result = {
            'success': True,
            'prospect': prospect_data,
            'email': email_data,
            'timestamp': time.time(),
            'status': PipelineConfig.STATUS_SUCCESS
        }
        
        if draft_result:
            result['draft_result'] = draft_result
            result['draft_id'] = draft_result.get('draft_id', 'N/A')
        
        return result
    
    def create_error_result(self, prospect_data: Dict[str, Any], 
                          error: str, 
                          failed_phase: str = None) -> Dict[str, Any]:
        """
        Create an error result object
        
        Args:
            prospect_data (Dict[str, Any]): Original prospect data
            error (str): Error message
            failed_phase (str, optional): Phase where error occurred
            
        Returns:
            Dict[str, Any]: Formatted error result
        """
        result = {
            'success': False,
            'prospect': prospect_data,
            'error': error,
            'timestamp': time.time(),
            'status': PipelineConfig.STATUS_ERROR
        }
        
        if failed_phase:
            result['failed_phase'] = failed_phase
        
        return result


# =============================================================================
# MAIN PIPELINE CLASS
# =============================================================================

class SimpleEmailPipeline:
    """
    Simplified email pipeline for cold email automation
    
    This class orchestrates the entire email processing workflow, managing
    the flow between different phases and coordinating all tools and agents.
    
    Processing Flow:
    1. Research → Gather company information
    2. Personalization → Match profile with job requirements  
    3. Email Writing → Generate personalized email content
    4. Quality Check → Review and improve email quality
    5. Draft Creation → Create email draft in Gmail (optional)
    
    Attributes:
        llm_provider (str): LLM provider to use (gemini/openai)
        tools (Dict[str, Any]): Available processing tools
        agents (Dict[str, Agent]): CrewAI agents for each phase
        phase_processor (PhaseProcessor): Handles individual phase processing
        result_manager (ResultManager): Manages result creation and formatting
    """
    
    def __init__(self, llm_provider: str = PipelineConfig.DEFAULT_LLM_PROVIDER):
        """
        Initialize the email pipeline
        
        Args:
            llm_provider (str): LLM provider to use for processing
        """
        self.logger = setup_logger('simple_pipeline')
        self.llm_provider = llm_provider
        
        self.logger.info(f"Initializing SimpleEmailPipeline with LLM provider: {llm_provider}")
        
        # Initialize components
        self._initialize_components()
        
        self.logger.info("SimpleEmailPipeline initialization completed")
    
    def _initialize_components(self):
        """Initialize all pipeline components"""
        # Initialize tools
        tool_manager = ToolManager()
        self.tools = tool_manager.get_tools()
        
        # Initialize agents
        agent_manager = AgentManager(self.tools)
        self.agents = agent_manager.create_all_agents()
        
        # Initialize processors
        self.phase_processor = PhaseProcessor(self.tools)
        self.result_manager = ResultManager()
    
    def process_prospect(self, prospect_data: Dict[str, Any], 
                        create_draft: bool = False, 
                        dry_run: bool = False) -> Dict[str, Any]:
        """
        Process a single prospect through the complete pipeline
        
        This method orchestrates the entire email processing workflow for a single
        prospect, handling all phases from research to final output.
        
        Args:
            prospect_data (Dict[str, Any]): Prospect information (name, email, company, role)
            create_draft (bool): Whether to create email draft (default: False)
            dry_run (bool): Whether to run in preview mode (default: False)
            
        Returns:
            Dict[str, Any]: Complete processing result with success/error status
            
        Example:
            >>> pipeline = SimpleEmailPipeline()
            >>> result = pipeline.process_prospect({
            ...     'name': 'John Doe',
            ...     'email': 'john@example.com',
            ...     'company': 'TechCorp',
            ...     'role': 'Software Engineer'
            ... }, create_draft=True)
        """
        prospect_name = prospect_data.get('name', 'Unknown')
        self.logger.info(f"Starting pipeline processing for prospect: {prospect_name}")
        
        try:
            # Phase 1: Research - Gather company information
            self.logger.info(f"Phase 1: Research for {prospect_name}")
            research_result = self.phase_processor.process_research_phase(prospect_data)
            if not research_result['success']:
                return self.result_manager.create_error_result(
                    prospect_data, research_result['error'], 'research'
                )
            
            # Phase 2: Personalization - Match profile with job requirements
            self.logger.info(f"Phase 2: Personalization for {prospect_name}")
            personalization_result = self.phase_processor.process_personalization_phase(
                prospect_data, research_result['data']
            )
            if not personalization_result['success']:
                return self.result_manager.create_error_result(
                    prospect_data, personalization_result['error'], 'personalization'
                )
            
            # Phase 3: Email Writing - Generate personalized email content
            self.logger.info(f"Phase 3: Email Writing for {prospect_name}")
            email_result = self.phase_processor.process_writing_phase(
                prospect_data, research_result['data'], personalization_result['data']
            )
            if not email_result['success']:
                return self.result_manager.create_error_result(
                    prospect_data, email_result['error'], 'writing'
                )
            
            # Phase 4: Quality Check - Review and improve email quality
            self.logger.info(f"Phase 4: Quality Check for {prospect_name}")
            quality_result = self.phase_processor.process_quality_phase(
                prospect_data, email_result['data']
            )
            if not quality_result['success']:
                return self.result_manager.create_error_result(
                    prospect_data, quality_result['error'], 'quality'
                )
            
            # Phase 5: Draft Creation or Preview - Final output phase
            if create_draft:
                self.logger.info(f"Phase 5: Draft Creation for {prospect_name}")
                draft_result = self.phase_processor.process_draft_creation_phase(
                    prospect_data, quality_result['data']
                )
                if not draft_result['success']:
                    return self.result_manager.create_error_result(
                        prospect_data, draft_result['error'], 'draft_creation'
                    )
                
                # Return success result with draft information
                return self.result_manager.create_success_result(
                    prospect_data, email_result['data'], draft_result['data']
                )
            
            elif not dry_run:
                # Send email directly (not implemented in this version)
                self.logger.warning("Direct email sending not implemented - use draft mode")
                return self.result_manager.create_error_result(
                    prospect_data, "Direct sending not implemented", 'sending'
                )
            
            else:
                # Preview mode - return success result without draft
                self.logger.info(f"Preview mode completed for {prospect_name}")
                return self.result_manager.create_success_result(
                    prospect_data, email_result['data'], None
                )
                
        except Exception as e:
            error_msg = f"Pipeline error: {str(e)}"
            self.logger.error(error_msg)
            return self.result_manager.create_error_result(prospect_data, error_msg)
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status and configuration
        
        Returns:
            Dict[str, Any]: Pipeline status information
        """
        return {
            'llm_provider': self.llm_provider,
            'tools_available': list(self.tools.keys()),
            'agents_available': list(self.agents.keys()),
            'phases': PipelineConfig.PHASES,
            'status': 'initialized'
        } 