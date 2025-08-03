"""
MCP Tool Base Class for CrewAI Cold Email Automation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from .mcp_context import MCPContext
import time
import json


@dataclass
class MCPToolResult:
    """Result from MCP tool execution"""
    success: bool
    data: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MCPToolBase(ABC):
    """Base class for all MCP tools"""
    
    def __init__(self, tool_name: str, tool_description: str):
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.required_context_keys: List[str] = []
        self.optional_context_keys: List[str] = []
    
    @abstractmethod
    def execute(self, context: MCPContext, **kwargs) -> MCPToolResult:
        """Execute the tool with given context and parameters"""
        pass
    
    def validate_context(self, context: MCPContext) -> bool:
        """Validate that context has required keys"""
        for key in self.required_context_keys:
            if not hasattr(context, key) or getattr(context, key) is None:
                return False
        return True
    
    def get_available_context_keys(self) -> List[str]:
        """Get all available context keys for this tool"""
        return self.required_context_keys + self.optional_context_keys
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """Get tool schema for registration"""
        return {
            'name': self.tool_name,
            'description': self.tool_description,
            'required_context_keys': self.required_context_keys,
            'optional_context_keys': self.optional_context_keys,
            'input_schema': self.get_input_schema(),
            'output_schema': self.get_output_schema()
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for the tool"""
        return {
            'type': 'object',
            'properties': {},
            'required': []
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema for the tool"""
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'data': {'type': 'object'},
                'error_message': {'type': 'string'},
                'execution_time': {'type': 'number'},
                'metadata': {'type': 'object'}
            }
        }
    
    def execute_with_timing(self, context: MCPContext, **kwargs) -> MCPToolResult:
        """Execute tool with timing and context recording"""
        start_time = time.time()
        
        try:
            # Validate context
            if not self.validate_context(context):
                return MCPToolResult(
                    success=False,
                    data={},
                    error_message=f"Missing required context keys: {self.required_context_keys}",
                    execution_time=time.time() - start_time
                )
            
            # Execute tool
            result = self.execute(context, **kwargs)
            result.execution_time = time.time() - start_time
            
            # Record tool call in context
            context.add_tool_call(
                tool_name=self.tool_name,
                input_data=kwargs,
                output_data=result.data,
                execution_time=result.execution_time
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_result = MCPToolResult(
                success=False,
                data={},
                error_message=str(e),
                execution_time=execution_time
            )
            
            # Record error in context
            context.add_error(f"Tool {self.tool_name} failed: {str(e)}")
            
            return error_result


class MCPToolRegistry:
    """Registry for MCP tools"""
    
    def __init__(self):
        self.tools: Dict[str, MCPToolBase] = {}
    
    def register_tool(self, tool: MCPToolBase):
        """Register a tool in the registry"""
        self.tools[tool.tool_name] = tool
    
    def get_tool(self, tool_name: str) -> Optional[MCPToolBase]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all registered tools"""
        return {
            name: tool.get_tool_schema() 
            for name, tool in self.tools.items()
        }
    
    def execute_tool(self, tool_name: str, context: MCPContext, **kwargs) -> MCPToolResult:
        """Execute a tool by name"""
        tool = self.get_tool(tool_name)
        if not tool:
            return MCPToolResult(
                success=False,
                data={},
                error_message=f"Tool '{tool_name}' not found",
                execution_time=0.0
            )
        
        return tool.execute_with_timing(context, **kwargs) 