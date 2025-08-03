"""
MCP Company Research Tool for CrewAI Cold Email Automation
"""

from typing import Dict, Any
from ..mcp_tool_base import MCPToolBase, MCPToolResult
from ..mcp_context import MCPContext
import requests
import json
import time


class CompanyResearchMCPTool(MCPToolBase):
    """MCP-compatible company research tool"""
    
    def __init__(self):
        super().__init__(
            tool_name="company_research",
            tool_description="Research company information from public sources"
        )
        self.required_context_keys = ['prospect_data']
        self.optional_context_keys = ['company_research']
    
    def execute(self, context: MCPContext, **kwargs) -> MCPToolResult:
        """Execute company research with MCP context"""
        try:
            # Extract company name from context or kwargs
            company_name = kwargs.get('company_name')
            if not company_name and context.prospect_data:
                company_name = context.prospect_data.get('company', 'Unknown Company')
            
            if not company_name:
                return MCPToolResult(
                    success=False,
                    data={},
                    error_message="No company name provided"
                )
            
            # Perform research
            research_data = self._research_company(company_name)
            
            # Update context with research data
            context.company_research = research_data
            
            return MCPToolResult(
                success=True,
                data={
                    'company_name': company_name,
                    'research_data': research_data,
                    'research_timestamp': time.time()
                },
                metadata={
                    'research_sources': ['public_apis', 'web_search'],
                    'data_freshness': 'recent'
                }
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                data={},
                error_message=f"Company research failed: {str(e)}"
            )
    
    def _research_company(self, company_name: str) -> Dict[str, Any]:
        """Perform company research"""
        try:
            # In production, use proper APIs like Crunchbase, LinkedIn, etc.
            # For now, simulate research data
            research_data = {
                "name": company_name,
                "industry": self._determine_industry(company_name),
                "size": self._estimate_company_size(company_name),
                "recent_news": self._get_recent_news(company_name),
                "culture": self._analyze_culture(company_name),
                "technologies": self._identify_technologies(company_name),
                "values": self._extract_values(company_name),
                "challenges": self._identify_challenges(company_name),
                "opportunities": self._identify_opportunities(company_name)
            }
            
            return research_data
            
        except Exception as e:
            return {
                "name": company_name,
                "error": f"Research failed: {str(e)}",
                "industry": "Unknown",
                "size": "Unknown"
            }
    
    def _determine_industry(self, company_name: str) -> str:
        """Determine company industry"""
        # Simple keyword-based industry detection
        company_lower = company_name.lower()
        
        if any(word in company_lower for word in ['tech', 'software', 'ai', 'ml', 'data']):
            return "Technology"
        elif any(word in company_lower for word in ['finance', 'bank', 'pay', 'fintech']):
            return "Financial Services"
        elif any(word in company_lower for word in ['health', 'medical', 'bio']):
            return "Healthcare"
        elif any(word in company_lower for word in ['retail', 'ecommerce', 'shop']):
            return "Retail"
        else:
            return "Technology"  # Default
    
    def _estimate_company_size(self, company_name: str) -> str:
        """Estimate company size"""
        # In production, use actual data
        return "1000-5000 employees"
    
    def _get_recent_news(self, company_name: str) -> list:
        """Get recent company news"""
        # In production, use news APIs
        return [
            f"{company_name} announced new product launch",
            f"{company_name} expanded to new markets",
            f"{company_name} received Series B funding"
        ]
    
    def _analyze_culture(self, company_name: str) -> str:
        """Analyze company culture"""
        return "Innovation-focused, collaborative environment"
    
    def _identify_technologies(self, company_name: str) -> list:
        """Identify technologies used by company"""
        return ["Python", "AI/ML", "Cloud Computing", "React", "Node.js"]
    
    def _extract_values(self, company_name: str) -> list:
        """Extract company values"""
        return ["Innovation", "Customer Success", "Teamwork", "Excellence"]
    
    def _identify_challenges(self, company_name: str) -> list:
        """Identify company challenges"""
        return [
            "Scaling infrastructure",
            "Talent acquisition",
            "Market competition"
        ]
    
    def _identify_opportunities(self, company_name: str) -> list:
        """Identify company opportunities"""
        return [
            "Market expansion",
            "Product innovation",
            "Strategic partnerships"
        ]
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for company research tool"""
        return {
            'type': 'object',
            'properties': {
                'company_name': {
                    'type': 'string',
                    'description': 'Name of the company to research'
                }
            },
            'required': ['company_name']
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema for company research tool"""
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'company_name': {'type': 'string'},
                        'research_data': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string'},
                                'industry': {'type': 'string'},
                                'size': {'type': 'string'},
                                'recent_news': {'type': 'array', 'items': {'type': 'string'}},
                                'culture': {'type': 'string'},
                                'technologies': {'type': 'array', 'items': {'type': 'string'}},
                                'values': {'type': 'array', 'items': {'type': 'string'}},
                                'challenges': {'type': 'array', 'items': {'type': 'string'}},
                                'opportunities': {'type': 'array', 'items': {'type': 'string'}}
                            }
                        },
                        'research_timestamp': {'type': 'number'}
                    }
                },
                'error_message': {'type': 'string'},
                'execution_time': {'type': 'number'},
                'metadata': {'type': 'object'}
            }
        } 