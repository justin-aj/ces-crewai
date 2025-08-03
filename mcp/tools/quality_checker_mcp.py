"""
MCP Quality Checker Tool for CrewAI Cold Email Automation
"""

from typing import Dict, Any
from ..mcp_tool_base import MCPToolBase, MCPToolResult
from ..mcp_context import MCPContext
import re


class QualityCheckerMCPTool(MCPToolBase):
    """MCP-compatible quality checker tool"""
    
    def __init__(self):
        super().__init__(
            tool_name="quality_checker",
            tool_description="Review and improve email quality, personalization, and effectiveness"
        )
        self.required_context_keys = ['email_draft', 'prospect_data']
        self.optional_context_keys = ['quality_metrics', 'company_research', 'profile_matches']
    
    def execute(self, context: MCPContext, **kwargs) -> MCPToolResult:
        """Execute quality check with MCP context"""
        try:
            email_draft = context.email_draft
            prospect_data = context.prospect_data
            
            if not email_draft:
                return MCPToolResult(
                    success=False,
                    data={},
                    error_message="No email draft found in context"
                )
            
            # Perform quality checks
            quality_metrics = self._perform_quality_checks(
                email_draft, prospect_data, context
            )
            
            # Generate improvement suggestions
            improvements = self._generate_improvements(quality_metrics, email_draft)
            
            # Update context
            context.quality_metrics = quality_metrics
            
            # Create final email with improvements
            final_email = self._apply_improvements(email_draft, improvements)
            context.email_draft = final_email
            
            return MCPToolResult(
                success=True,
                data={
                    'quality_metrics': quality_metrics,
                    'improvements': improvements,
                    'final_email': final_email,
                    'overall_score': self._calculate_overall_score(quality_metrics)
                },
                metadata={
                    'checks_performed': len(quality_metrics),
                    'improvements_applied': len(improvements)
                }
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                data={},
                error_message=f"Quality check failed: {str(e)}"
            )
    
    def _perform_quality_checks(self, email_draft: Dict[str, Any], 
                               prospect_data: Dict[str, Any],
                               context: MCPContext) -> Dict[str, Any]:
        """Perform comprehensive quality checks"""
        metrics = {}
        
        # Personalization checks
        metrics['personalization'] = self._check_personalization(email_draft, prospect_data, context)
        
        # Grammar and style checks
        metrics['grammar_style'] = self._check_grammar_style(email_draft)
        
        # Length and structure checks
        metrics['length_structure'] = self._check_length_structure(email_draft)
        
        # Professionalism checks
        metrics['professionalism'] = self._check_professionalism(email_draft)
        
        # Call-to-action checks
        metrics['call_to_action'] = self._check_call_to_action(email_draft)
        
        # Company-specific checks
        metrics['company_specific'] = self._check_company_specific(email_draft, context)
        
        return metrics
    
    def _check_personalization(self, email_draft: Dict[str, Any], 
                             prospect_data: Dict[str, Any],
                             context: MCPContext) -> Dict[str, Any]:
        """Check personalization quality"""
        body = email_draft.get('body', '')
        subject = email_draft.get('subject', '')
        
        checks = {
            'prospect_name_used': False,
            'company_mentioned': False,
            'position_mentioned': False,
            'specific_details': False,
            'score': 0.0
        }
        
        # Check for prospect name usage
        prospect_name = prospect_data.get('name', '')
        if prospect_name and prospect_name.lower() in body.lower():
            checks['prospect_name_used'] = True
            checks['score'] += 0.2
        
        # Check for company mentions
        company_name = prospect_data.get('company', '')
        if company_name and company_name.lower() in body.lower():
            checks['company_mentioned'] = True
            checks['score'] += 0.2
        
        # Check for position mentions
        position = prospect_data.get('position', '')
        if position and position.lower() in body.lower():
            checks['position_mentioned'] = True
            checks['score'] += 0.2
        
        # Check for specific details (not generic)
        generic_phrases = [
            'your company', 'your team', 'this role', 'this position',
            'your organization', 'your business'
        ]
        
        specific_count = 0
        for phrase in generic_phrases:
            if phrase.lower() in body.lower():
                specific_count += 1
        
        if specific_count < 2:  # Not too generic
            checks['specific_details'] = True
            checks['score'] += 0.4
        
        return checks
    
    def _check_grammar_style(self, email_draft: Dict[str, Any]) -> Dict[str, Any]:
        """Check grammar and style"""
        body = email_draft.get('body', '')
        subject = email_draft.get('subject', '')
        
        checks = {
            'grammar_errors': 0,
            'spelling_errors': 0,
            'sentence_length': 'good',
            'tone_appropriate': True,
            'score': 0.0
        }
        
        # Basic grammar checks
        sentences = re.split(r'[.!?]+', body)
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Check for common grammar issues
                if sentence.count('I') > 3:  # Too many "I" statements
                    checks['grammar_errors'] += 1
                
                if len(sentence.split()) > 25:  # Long sentences
                    checks['grammar_errors'] += 1
        
        # Check sentence length
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
        if avg_sentence_length > 20:
            checks['sentence_length'] = 'long'
        elif avg_sentence_length < 8:
            checks['sentence_length'] = 'short'
        
        # Calculate score
        checks['score'] = max(0.0, 1.0 - (checks['grammar_errors'] * 0.1))
        
        return checks
    
    def _check_length_structure(self, email_draft: Dict[str, Any]) -> Dict[str, Any]:
        """Check email length and structure"""
        body = email_draft.get('body', '')
        subject = email_draft.get('subject', '')
        
        checks = {
            'body_length': len(body),
            'subject_length': len(subject),
            'paragraphs': len(body.split('\n\n')),
            'length_appropriate': True,
            'structure_good': True,
            'score': 0.0
        }
        
        # Check body length
        if len(body) < 100:
            checks['length_appropriate'] = False
        elif len(body) > 500:
            checks['length_appropriate'] = False
        
        # Check subject length
        if len(subject) < 10 or len(subject) > 60:
            checks['length_appropriate'] = False
        
        # Check structure
        if checks['paragraphs'] < 3 or checks['paragraphs'] > 8:
            checks['structure_good'] = False
        
        # Calculate score
        score = 0.0
        if checks['length_appropriate']:
            score += 0.5
        if checks['structure_good']:
            score += 0.5
        
        checks['score'] = score
        
        return checks
    
    def _check_professionalism(self, email_draft: Dict[str, Any]) -> Dict[str, Any]:
        """Check professionalism"""
        body = email_draft.get('body', '').lower()
        subject = email_draft.get('subject', '').lower()
        
        checks = {
            'professional_tone': True,
            'no_spam_words': True,
            'appropriate_formality': True,
            'score': 0.0
        }
        
        # Check for spam words
        spam_words = [
            'urgent', 'limited time', 'act now', 'exclusive offer',
            'free', 'guaranteed', 'no risk', 'once in a lifetime'
        ]
        
        for word in spam_words:
            if word in body or word in subject:
                checks['no_spam_words'] = False
                break
        
        # Check formality
        informal_words = ['hey', 'hi there', 'whats up', 'cool', 'awesome']
        for word in informal_words:
            if word in body:
                checks['appropriate_formality'] = False
                break
        
        # Calculate score
        score = 0.0
        if checks['professional_tone']:
            score += 0.3
        if checks['no_spam_words']:
            score += 0.4
        if checks['appropriate_formality']:
            score += 0.3
        
        checks['score'] = score
        
        return checks
    
    def _check_call_to_action(self, email_draft: Dict[str, Any]) -> Dict[str, Any]:
        """Check call-to-action quality"""
        body = email_draft.get('body', '').lower()
        
        checks = {
            'has_cta': False,
            'cta_clear': False,
            'cta_specific': False,
            'score': 0.0
        }
        
        # Check for CTA presence
        cta_indicators = [
            'would love to', 'interested in', 'available for', 'free for',
            'can we', 'would you be', 'let\'s discuss', 'schedule a call'
        ]
        
        for indicator in cta_indicators:
            if indicator in body:
                checks['has_cta'] = True
                break
        
        # Check CTA clarity
        if checks['has_cta']:
            checks['cta_clear'] = True
        
        # Check CTA specificity
        specific_indicators = ['this week', 'next week', 'call', 'meeting', 'discussion']
        for indicator in specific_indicators:
            if indicator in body:
                checks['cta_specific'] = True
                break
        
        # Calculate score
        score = 0.0
        if checks['has_cta']:
            score += 0.4
        if checks['cta_clear']:
            score += 0.3
        if checks['cta_specific']:
            score += 0.3
        
        checks['score'] = score
        
        return checks
    
    def _check_company_specific(self, email_draft: Dict[str, Any], 
                               context: MCPContext) -> Dict[str, Any]:
        """Check company-specific content"""
        body = email_draft.get('body', '').lower()
        company_research = context.company_research
        
        checks = {
            'company_values_mentioned': False,
            'recent_news_mentioned': False,
            'industry_specific': False,
            'score': 0.0
        }
        
        if company_research:
            # Check for company values
            values = company_research.get('values', [])
            for value in values:
                if value.lower() in body:
                    checks['company_values_mentioned'] = True
                    break
            
            # Check for recent news
            news = company_research.get('recent_news', [])
            for news_item in news:
                if any(word.lower() in body for word in news_item.lower().split()[:3]):
                    checks['recent_news_mentioned'] = True
                    break
            
            # Check for industry-specific content
            industry = company_research.get('industry', '').lower()
            if industry and industry in body:
                checks['industry_specific'] = True
        
        # Calculate score
        score = 0.0
        if checks['company_values_mentioned']:
            score += 0.4
        if checks['recent_news_mentioned']:
            score += 0.4
        if checks['industry_specific']:
            score += 0.2
        
        checks['score'] = score
        
        return checks
    
    def _generate_improvements(self, quality_metrics: Dict[str, Any], 
                             email_draft: Dict[str, Any]) -> list:
        """Generate improvement suggestions"""
        improvements = []
        
        # Personalization improvements
        personalization = quality_metrics.get('personalization', {})
        if personalization.get('score', 0) < 0.7:
            improvements.append("Add more specific details about the company and role")
        
        # Grammar improvements
        grammar = quality_metrics.get('grammar_style', {})
        if grammar.get('grammar_errors', 0) > 0:
            improvements.append("Review sentence structure and grammar")
        
        # Length improvements
        length = quality_metrics.get('length_structure', {})
        if not length.get('length_appropriate', True):
            if length.get('body_length', 0) < 100:
                improvements.append("Add more detail to make email more substantial")
            else:
                improvements.append("Consider shortening email for better readability")
        
        # Professionalism improvements
        professionalism = quality_metrics.get('professionalism', {})
        if not professionalism.get('no_spam_words', True):
            improvements.append("Remove marketing language and focus on professional tone")
        
        # CTA improvements
        cta = quality_metrics.get('call_to_action', {})
        if not cta.get('has_cta', False):
            improvements.append("Add a clear call-to-action")
        elif not cta.get('cta_specific', False):
            improvements.append("Make call-to-action more specific with time/action")
        
        return improvements
    
    def _apply_improvements(self, email_draft: Dict[str, Any], 
                           improvements: list) -> Dict[str, Any]:
        """Apply improvements to email draft"""
        # For now, return the original draft
        # In production, implement actual improvements
        return email_draft
    
    def _calculate_overall_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        scores = []
        
        for category, metrics in quality_metrics.items():
            if isinstance(metrics, dict) and 'score' in metrics:
                scores.append(metrics['score'])
        
        if scores:
            return sum(scores) / len(scores)
        else:
            return 0.0
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for quality checker tool"""
        return {
            'type': 'object',
            'properties': {
                'email_draft': {
                    'type': 'object',
                    'description': 'Email draft to check'
                },
                'prospect_data': {
                    'type': 'object',
                    'description': 'Prospect information'
                }
            },
            'required': ['email_draft']
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema for quality checker tool"""
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'quality_metrics': {'type': 'object'},
                        'improvements': {'type': 'array', 'items': {'type': 'string'}},
                        'final_email': {'type': 'object'},
                        'overall_score': {'type': 'number'}
                    }
                },
                'error_message': {'type': 'string'},
                'execution_time': {'type': 'number'},
                'metadata': {'type': 'object'}
            }
        } 