"""
MCP Agent Factory for CrewAI Cold Email Automation
"""

from crewai import Agent
from typing import Dict, Any, List, Optional
from .mcp_context import MCPContext
from .mcp_tool_registry import MCPToolRegistry
import yaml
import os


class MCPAgentFactory:
    """Factory for creating CrewAI agents with MCP tool integration"""
    
    def __init__(self, tool_registry: MCPToolRegistry, llm_provider='gemini'):
        self.tool_registry = tool_registry
        self.llm_provider = llm_provider
        self.agent_configs = self._load_agent_configs()
        self.llm = self._initialize_llm()
    
    def _load_agent_configs(self) -> Dict[str, Any]:
        """Load agent configurations from YAML"""
        with open('configs/agent_config.yaml', 'r') as f:
            return yaml.safe_load(f)
    
    def _initialize_llm(self):
        """Initialize LLM based on provider"""
        if self.llm_provider == 'gemini':
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=os.getenv('GOOGLE_API_KEY')
            )
        else:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model="gpt-4",
                openai_api_key=os.getenv('OPENAI_API_KEY')
            )
    
    def create_agent_with_mcp_tools(self, agent_type: str, 
                                   tool_categories: List[str] = None,
                                   custom_tools: List[str] = None) -> Agent:
        """Create a CrewAI agent with MCP tools"""
        
        if agent_type not in self.agent_configs:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        config = self.agent_configs[agent_type]
        
        # Get tools for this agent
        tools = self._get_tools_for_agent(agent_type, tool_categories, custom_tools)
        
        # Create CrewAI agent
        agent = Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        return agent
    
    def _get_tools_for_agent(self, agent_type: str, 
                            tool_categories: List[str] = None,
                            custom_tools: List[str] = None) -> List:
        """Get tools appropriate for a specific agent type"""
        tools = []
        
        # Add tools based on agent type
        if agent_type == 'researcher':
            tools.extend(self._get_research_tools())
        elif agent_type == 'personalizer':
            tools.extend(self._get_personalization_tools())
        elif agent_type == 'email_writer':
            tools.extend(self._get_writing_tools())
        elif agent_type == 'quality_checker':
            tools.extend(self._get_quality_tools())
        
        # Add tools from specified categories
        if tool_categories:
            for category in tool_categories:
                category_tools = self.tool_registry.get_tools_by_category(category)
                for tool_name in category_tools:
                    tool = self.tool_registry.get_tool(tool_name)
                    if tool:
                        tools.append(tool)
        
        # Add custom tools
        if custom_tools:
            for tool_name in custom_tools:
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    tools.append(tool)
        
        return tools
    
    def _get_research_tools(self) -> List:
        """Get tools for research agent"""
        research_tools = []
        
        # Add company research tool
        company_research_tool = self.tool_registry.get_tool('company_research')
        if company_research_tool:
            research_tools.append(company_research_tool)
        
        # Add other research-related tools
        research_category_tools = self.tool_registry.get_tools_by_category('research')
        for tool_name in research_category_tools:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                research_tools.append(tool)
        
        return research_tools
    
    def _get_personalization_tools(self) -> List:
        """Get tools for personalization agent"""
        personalization_tools = []
        
        # Add profile matcher tool
        profile_matcher_tool = self.tool_registry.get_tool('profile_matcher')
        if profile_matcher_tool:
            personalization_tools.append(profile_matcher_tool)
        
        # Add other personalization-related tools
        personalization_category_tools = self.tool_registry.get_tools_by_category('personalization')
        for tool_name in personalization_category_tools:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                personalization_tools.append(tool)
        
        return personalization_tools
    
    def _get_writing_tools(self) -> List:
        """Get tools for email writing agent"""
        writing_tools = []
        
        # Add email writing tools
        writing_category_tools = self.tool_registry.get_tools_by_category('writing')
        for tool_name in writing_category_tools:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                writing_tools.append(tool)
        
        return writing_tools
    
    def _get_quality_tools(self) -> List:
        """Get tools for quality checking agent"""
        quality_tools = []
        
        # Add quality checking tools
        quality_category_tools = self.tool_registry.get_tools_by_category('quality')
        for tool_name in quality_category_tools:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                quality_tools.append(tool)
        
        return quality_tools
    
    def create_pipeline_agents(self) -> Dict[str, Agent]:
        """Create all agents needed for the email pipeline"""
        agents = {}
        
        agent_types = ['researcher', 'personalizer', 'email_writer', 'quality_checker']
        
        for agent_type in agent_types:
            agents[agent_type] = self.create_agent_with_mcp_tools(agent_type)
        
        return agents
    
    def get_agent_capabilities(self, agent_type: str) -> Dict[str, Any]:
        """Get capabilities of a specific agent type"""
        if agent_type not in self.agent_configs:
            return {}
        
        config = self.agent_configs[agent_type]
        tools = self._get_tools_for_agent(agent_type)
        
        return {
            'role': config['role'],
            'goal': config['goal'],
            'available_tools': [tool.tool_name for tool in tools],
            'tool_categories': self._get_tool_categories_for_agent(agent_type)
        }
    
    def _get_tool_categories_for_agent(self, agent_type: str) -> List[str]:
        """Get tool categories for a specific agent"""
        if agent_type == 'researcher':
            return ['research']
        elif agent_type == 'personalizer':
            return ['personalization']
        elif agent_type == 'email_writer':
            return ['writing']
        elif agent_type == 'quality_checker':
            return ['quality']
        else:
            return [] 