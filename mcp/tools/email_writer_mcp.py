"""
MCP Email Writer Tool for CrewAI Cold Email Automation
"""

from typing import Dict, Any
from ..mcp_tool_base import MCPToolBase, MCPToolResult
from ..mcp_context import MCPContext
import yaml
import json


class EmailWriterMCPTool(MCPToolBase):
    """MCP-compatible email writer tool"""
    
    def __init__(self):
        super().__init__(
            tool_name="email_writer",
            tool_description="Write personalized cold emails based on research and personalization data"
        )
        self.required_context_keys = ['prospect_data', 'company_research', 'profile_matches']
        self.optional_context_keys = ['email_draft', 'personalization_strategy']
        self.templates_path = 'templates/email_templates.yaml'
    
    def execute(self, context: MCPContext, **kwargs) -> MCPToolResult:
        """Execute email writing with MCP context"""
        try:
            # Load email templates
            templates = self._load_email_templates()
            if not templates:
                return MCPToolResult(
                    success=False,
                    data={},
                    error_message="Failed to load email templates"
                )
            
            # Extract data from context
            prospect_data = context.prospect_data
            company_research = context.company_research
            profile_matches = context.profile_matches
            personalization_strategy = context.personalization_strategy
            
            # Write email
            email_data = self._write_personalized_email(
                prospect_data, company_research, profile_matches, 
                personalization_strategy, templates
            )
            
            # Update context
            context.email_draft = email_data
            
            return MCPToolResult(
                success=True,
                data=email_data,
                metadata={
                    'template_used': email_data.get('template_type', 'professional_application'),
                    'personalization_level': self._calculate_personalization_level(email_data),
                    'email_length': len(email_data.get('body', ''))
                }
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                data={},
                error_message=f"Email writing failed: {str(e)}"
            )
    
    def _load_email_templates(self) -> Dict[str, Any]:
        """Load email templates from YAML file"""
        try:
            with open(self.templates_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading templates: {str(e)}")
            return None
    
    def _write_personalized_email(self, prospect_data: Dict[str, Any],
                                company_research: Dict[str, Any],
                                profile_matches: Dict[str, Any],
                                personalization_strategy: Dict[str, Any],
                                templates: Dict[str, Any]) -> Dict[str, Any]:
        """Write personalized email based on all available data"""
        
        # Determine template type based on company research
        template_type = self._select_template_type(company_research)
        template = templates.get(template_type, templates.get('professional_application'))
        
        # Generate subject line
        subject = self._generate_subject_line(prospect_data, company_research, template_type)
        
        # Generate email body
        body = self._generate_email_body(
            prospect_data, company_research, profile_matches, 
            personalization_strategy, template
        )
        
        return {
            'subject': subject,
            'body': body,
            'template_type': template_type,
            'personalization_data': {
                'company_mentions': self._extract_company_mentions(body),
                'skill_mentions': self._extract_skill_mentions(body),
                'achievement_mentions': self._extract_achievement_mentions(body)
            }
        }
    
    def _select_template_type(self, company_research: Dict[str, Any]) -> str:
        """Select appropriate email template based on company research"""
        industry = company_research.get('industry', '').lower()
        size = company_research.get('size', '').lower()
        
        if 'startup' in size or 'early' in size:
            return 'tech_startup'
        elif 'enterprise' in size or 'large' in size:
            return 'enterprise'
        else:
            return 'professional_application'
    
    def _generate_subject_line(self, prospect_data: Dict[str, Any],
                             company_research: Dict[str, Any], template_type: str) -> str:
        """Generate personalized subject line"""
        position = prospect_data.get('position', '')
        company = prospect_data.get('company', '')
        
        if template_type == 'tech_startup':
            return f"Scaling {company}'s {position} - Your Mission Resonates"
        elif template_type == 'enterprise':
            return f"Enterprise {position} - Reducing Risk for {company}"
        else:
            return f"Application for {position} at {company}"
    
    def _generate_email_body(self, prospect_data: Dict[str, Any],
                           company_research: Dict[str, Any],
                           profile_matches: Dict[str, Any],
                           personalization_strategy: Dict[str, Any],
                           template: Dict[str, Any]) -> str:
        """Generate personalized email body"""
        
        # Extract key information
        prospect_name = prospect_data.get('name', 'there')
        company_name = prospect_data.get('company', 'your company')
        position = prospect_data.get('position', 'this role')
        
        # Get personalization data
        direct_matches = profile_matches.get('direct_matches', [])
        achievements = profile_matches.get('achievement_matches', [])
        unique_strengths = profile_matches.get('unique_strengths', [])
        
        # Build email content
        email_parts = []
        
        # Opening
        opening = self._create_opening(prospect_name, company_name, company_research)
        email_parts.append(opening)
        
        # Introduction
        intro = self._create_introduction(profile_matches)
        email_parts.append(intro)
        
        # Value propositions
        value_props = self._create_value_propositions(direct_matches, achievements, unique_strengths)
        email_parts.extend(value_props)
        
        # Connection to company
        connection = self._create_company_connection(company_research, personalization_strategy)
        email_parts.append(connection)
        
        # Call to action
        cta = self._create_call_to_action(company_name, position)
        email_parts.append(cta)
        
        # Closing
        closing = self._create_closing()
        email_parts.append(closing)
        
        return '\n\n'.join(email_parts)
    
    def _create_opening(self, prospect_name: str, company_name: str, 
                       company_research: Dict[str, Any]) -> str:
        """Create personalized opening"""
        recent_news = company_research.get('recent_news', [])
        
        if recent_news:
            news_item = recent_news[0]
            return f"Hi {prospect_name},\n\n{news_item} - congratulations! I've been following {company_name}'s growth and am impressed by your innovative approach."
        else:
            return f"Hi {prospect_name},\n\nI've been researching {company_name} and am excited about the work you're doing."
    
    def _create_introduction(self, profile_matches: Dict[str, Any]) -> str:
        """Create personalized introduction"""
        experience_relevance = profile_matches.get('experience_relevance', 0.0)
        
        if experience_relevance > 0.8:
            return "I'm a senior software engineer with 7+ years of experience building scalable applications, and I believe my background aligns perfectly with your needs."
        else:
            return "I'm a software engineer passionate about solving complex technical challenges, and I'm excited about the opportunity to contribute to your team."
    
    def _create_value_propositions(self, direct_matches: list, achievements: list, 
                                 unique_strengths: list) -> list:
        """Create value propositions"""
        props = []
        
        # Add direct skill matches
        if direct_matches:
            skills_text = ', '.join(direct_matches[:3])
            props.append(f"• Deep expertise in {skills_text}")
        
        # Add achievements
        if achievements:
            for achievement in achievements[:2]:
                if isinstance(achievement, dict):
                    desc = achievement.get('description', str(achievement))
                else:
                    desc = str(achievement)
                props.append(f"• {desc}")
        
        # Add unique strengths
        if unique_strengths:
            strengths_text = ', '.join(unique_strengths[:2])
            props.append(f"• Unique perspective with {strengths_text}")
        
        return props
    
    def _create_company_connection(self, company_research: Dict[str, Any],
                                 personalization_strategy: Dict[str, Any]) -> str:
        """Create connection to company mission/values"""
        values = company_research.get('values', [])
        challenges = company_research.get('challenges', [])
        
        if values:
            value_text = ', '.join(values[:2])
            return f"Your values of {value_text} resonate with my approach to building sustainable, scalable solutions."
        elif challenges:
            challenge = challenges[0]
            return f"I'm particularly interested in helping {challenge} and believe my experience could accelerate your objectives."
        else:
            return "I'm excited about the opportunity to contribute to your mission and help drive innovation."
    
    def _create_call_to_action(self, company_name: str, position: str) -> str:
        """Create call to action"""
        return f"Would love to discuss how I could help {company_name} scale efficiently in the {position} role. Free for a quick call this week?"
    
    def _create_closing(self) -> str:
        """Create professional closing"""
        return "Best regards,\nJohn Smith"
    
    def _extract_company_mentions(self, body: str) -> list:
        """Extract company mentions from email body"""
        # Simple extraction - in production, use NLP
        return []
    
    def _extract_skill_mentions(self, body: str) -> list:
        """Extract skill mentions from email body"""
        # Simple extraction - in production, use NLP
        return []
    
    def _extract_achievement_mentions(self, body: str) -> list:
        """Extract achievement mentions from email body"""
        # Simple extraction - in production, use NLP
        return []
    
    def _calculate_personalization_level(self, email_data: Dict[str, Any]) -> float:
        """Calculate personalization level of the email"""
        # Simple scoring based on content
        personalization_data = email_data.get('personalization_data', {})
        
        score = 0.0
        if personalization_data.get('company_mentions'):
            score += 0.3
        if personalization_data.get('skill_mentions'):
            score += 0.3
        if personalization_data.get('achievement_mentions'):
            score += 0.4
        
        return min(score, 1.0)
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for email writer tool"""
        return {
            'type': 'object',
            'properties': {
                'prospect_data': {
                    'type': 'object',
                    'description': 'Prospect information'
                },
                'research_data': {
                    'type': 'object',
                    'description': 'Company research data'
                },
                'personalization_data': {
                    'type': 'object',
                    'description': 'Personalization strategy data'
                }
            },
            'required': ['prospect_data']
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema for email writer tool"""
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'subject': {'type': 'string'},
                        'body': {'type': 'string'},
                        'template_type': {'type': 'string'},
                        'personalization_data': {'type': 'object'}
                    }
                },
                'error_message': {'type': 'string'},
                'execution_time': {'type': 'number'},
                'metadata': {'type': 'object'}
            }
        } 