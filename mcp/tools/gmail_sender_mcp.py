"""
MCP Gmail Sender Tool for CrewAI Cold Email Automation
"""

from typing import Dict, Any, List
from ..mcp_tool_base import MCPToolBase, MCPToolResult
from ..mcp_context import MCPContext
import os
import json


class GmailSenderMCPTool(MCPToolBase):
    """MCP-compatible Gmail sender tool"""
    
    def __init__(self):
        super().__init__(
            tool_name="gmail_sender",
            tool_description="Send emails via Gmail API with rate limiting and tracking"
        )
        self.required_context_keys = ['email_draft', 'prospect_data']
        self.optional_context_keys = ['send_result']
        self.credentials_file = 'configs/credentials.json'
        self.rate_limit_config = self._load_rate_limit_config()
    
    def execute(self, context: MCPContext, **kwargs) -> MCPToolResult:
        """Execute email sending with MCP context"""
        try:
            # Extract email data
            email_draft = context.email_draft
            prospect_data = context.prospect_data
            
            if not email_draft:
                return MCPToolResult(
                    success=False,
                    data={},
                    error_message="No email draft found in context"
                )
            
            # Extract sending parameters
            to_email = kwargs.get('to_email') or prospect_data.get('email')
            subject = kwargs.get('subject') or email_draft.get('subject')
            body = kwargs.get('body') or email_draft.get('body')
            
            if not to_email:
                return MCPToolResult(
                    success=False,
                    data={},
                    error_message="No recipient email address provided"
                )
            
            # Check rate limits
            rate_check = self._check_rate_limits()
            if not rate_check['can_send']:
                return MCPToolResult(
                    success=False,
                    data={},
                    error_message=f"Rate limit exceeded: {rate_check['message']}"
                )
            
            # Send email
            send_result = self._send_email(to_email, subject, body, context)
            
            # Update context
            context.send_result = send_result
            
            return MCPToolResult(
                success=True,
                data=send_result,
                metadata={
                    'rate_limit_remaining': rate_check['remaining'],
                    'email_sent': True,
                    'recipient': to_email
                }
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                data={},
                error_message=f"Email sending failed: {str(e)}"
            )
    
    def _load_rate_limit_config(self) -> Dict[str, Any]:
        """Load rate limiting configuration"""
        try:
            with open('configs/email_config.yaml', 'r') as f:
                import yaml
                config = yaml.safe_load(f)
                return config.get('sending', {}).get('rate_limit', {})
        except Exception:
            return {
                'emails_per_hour': 20,
                'emails_per_day': 100,
                'delay_between_emails': 45
            }
    
    def _check_rate_limits(self) -> Dict[str, Any]:
        """Check if we can send an email based on rate limits"""
        # In production, implement actual rate limiting with persistent storage
        # For now, return a simple check
        return {
            'can_send': True,
            'remaining': {
                'hourly': 19,
                'daily': 99
            },
            'message': 'Rate limits OK'
        }
    
    def _send_email(self, to_email: str, subject: str, body: str, 
                   context: MCPContext) -> Dict[str, Any]:
        """Send email via Gmail API"""
        try:
            # In production, implement actual Gmail API integration
            # For now, simulate sending
            
            # Validate email format
            if not self._validate_email(to_email):
                return {
                    'success': False,
                    'error': 'Invalid email format',
                    'message_id': None,
                    'sent_at': None
                }
            
            # Simulate API call
            message_id = f"msg_{context.context_id}_{int(time.time())}"
            
            # Record send attempt
            send_result = {
                'success': True,
                'message_id': message_id,
                'sent_at': time.time(),
                'recipient': to_email,
                'subject': subject,
                'body_length': len(body),
                'status': 'sent'
            }
            
            # Log the send
            self._log_email_send(send_result, context)
            
            return send_result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message_id': None,
                'sent_at': None
            }
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _log_email_send(self, send_result: Dict[str, Any], context: MCPContext):
        """Log email send for tracking"""
        log_entry = {
            'timestamp': time.time(),
            'context_id': context.context_id,
            'prospect': context.prospect_data.get('name', 'Unknown'),
            'company': context.prospect_data.get('company', 'Unknown'),
            'email': send_result['recipient'],
            'subject': send_result['subject'],
            'status': send_result['status'],
            'message_id': send_result.get('message_id')
        }
        
        # In production, save to database or file
        # For now, just print
        print(f"Email sent: {log_entry}")
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for Gmail sender tool"""
        return {
            'type': 'object',
            'properties': {
                'to_email': {
                    'type': 'string',
                    'description': 'Recipient email address'
                },
                'subject': {
                    'type': 'string',
                    'description': 'Email subject line'
                },
                'body': {
                    'type': 'string',
                    'description': 'Email body content'
                }
            },
            'required': ['to_email']
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema for Gmail sender tool"""
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'message_id': {'type': 'string'},
                        'sent_at': {'type': 'number'},
                        'recipient': {'type': 'string'},
                        'subject': {'type': 'string'},
                        'body_length': {'type': 'number'},
                        'status': {'type': 'string'},
                        'error': {'type': 'string'}
                    }
                },
                'error_message': {'type': 'string'},
                'execution_time': {'type': 'number'},
                'metadata': {'type': 'object'}
            }
        }


# Import time module for timestamp generation
import time 