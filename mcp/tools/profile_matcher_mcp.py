"""
MCP Profile Matcher Tool for CrewAI Cold Email Automation
"""

from typing import Dict, Any
from ..mcp_tool_base import MCPToolBase, MCPToolResult
from ..mcp_context import MCPContext
import yaml
import json


class ProfileMatcherMCPTool(MCPToolBase):
    """MCP-compatible profile matcher tool"""
    
    def __init__(self):
        super().__init__(
            tool_name="profile_matcher",
            tool_description="Match user profile with job requirements for personalization"
        )
        self.required_context_keys = ['prospect_data']
        self.optional_context_keys = ['profile_matches', 'personalization_strategy']
        self.profile_path = 'data/my_profile.yaml'
    
    def execute(self, context: MCPContext, **kwargs) -> MCPToolResult:
        """Execute profile matching with MCP context"""
        try:
            # Load user profile
            user_profile = self._load_user_profile()
            if not user_profile:
                return MCPToolResult(
                    success=False,
                    data={},
                    error_message="Failed to load user profile"
                )
            
            # Extract job requirements
            job_requirements = kwargs.get('job_requirements', '')
            position = kwargs.get('position', '')
            
            if not job_requirements:
                job_requirements = context.prospect_data.get('job_description', '')
            if not position:
                position = context.prospect_data.get('position', '')
            
            # Perform matching
            matches = self._match_profile_to_job(user_profile, job_requirements, position)
            
            # Update context
            context.profile_matches = matches
            context.personalization_strategy = self._create_personalization_strategy(matches)
            
            return MCPToolResult(
                success=True,
                data={
                    'matches': matches,
                    'personalization_strategy': context.personalization_strategy,
                    'match_confidence': self._calculate_confidence(matches)
                },
                metadata={
                    'profile_loaded': True,
                    'matching_algorithm': 'skill_based'
                }
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                data={},
                error_message=f"Profile matching failed: {str(e)}"
            )
    
    def _load_user_profile(self) -> Dict[str, Any]:
        """Load user profile from YAML file"""
        try:
            with open(self.profile_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading profile: {str(e)}")
            return None
    
    def _match_profile_to_job(self, user_profile: Dict[str, Any], 
                             job_requirements: str, position: str) -> Dict[str, Any]:
        """Match user profile with job requirements"""
        matches = {
            'direct_matches': [],
            'related_matches': [],
            'missing_skills': [],
            'unique_strengths': [],
            'achievement_matches': [],
            'experience_relevance': 0.0,
            'skill_coverage': 0.0
        }
        
        # Extract skills from user profile
        user_skills = set()
        if 'skills' in user_profile:
            for category, skills in user_profile['skills'].items():
                if isinstance(skills, list):
                    user_skills.update(skills)
                elif isinstance(skills, str):
                    user_skills.add(skills)
        
        # Extract required skills from job description
        required_skills = self._extract_skills_from_text(job_requirements)
        
        # Direct matches
        matches['direct_matches'] = list(user_skills & set(required_skills))
        
        # Missing skills
        matches['missing_skills'] = list(set(required_skills) - user_skills)
        
        # Related matches
        matches['related_matches'] = self._find_related_matches(user_skills, required_skills)
        
        # Unique strengths
        matches['unique_strengths'] = list(user_skills - set(required_skills))
        
        # Achievement matches
        matches['achievement_matches'] = self._match_achievements(user_profile, job_requirements)
        
        # Calculate relevance scores
        matches['experience_relevance'] = self._calculate_experience_relevance(user_profile, position)
        matches['skill_coverage'] = len(matches['direct_matches']) / max(len(required_skills), 1)
        
        return matches
    
    def _extract_skills_from_text(self, text: str) -> list:
        """Extract skills from job description text"""
        # Simple keyword extraction - in production, use NLP
        skill_keywords = [
            'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'Django',
            'AWS', 'Docker', 'Kubernetes', 'SQL', 'MongoDB', 'Redis',
            'Machine Learning', 'AI', 'Data Science', 'DevOps', 'Agile',
            'REST API', 'GraphQL', 'Microservices', 'CI/CD'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _find_related_matches(self, user_skills: set, required_skills: list) -> list:
        """Find related skill matches"""
        skill_relations = {
            'Python': ['Django', 'Flask', 'FastAPI', 'Pandas', 'NumPy'],
            'JavaScript': ['React', 'Node.js', 'Vue.js', 'Angular', 'TypeScript'],
            'Machine Learning': ['AI', 'Deep Learning', 'Data Science', 'TensorFlow', 'PyTorch'],
            'AWS': ['Cloud Computing', 'Docker', 'Kubernetes', 'DevOps'],
            'SQL': ['Database', 'PostgreSQL', 'MySQL', 'MongoDB']
        }
        
        related_matches = []
        for user_skill in user_skills:
            related = skill_relations.get(user_skill, [])
            for related_skill in related:
                if related_skill in required_skills:
                    related_matches.append(related_skill)
        
        return list(set(related_matches))
    
    def _match_achievements(self, user_profile: Dict[str, Any], job_requirements: str) -> list:
        """Match user achievements with job requirements"""
        achievements = user_profile.get('achievements', [])
        relevant_achievements = []
        
        # Simple keyword matching
        requirement_keywords = job_requirements.lower().split()
        
        for achievement in achievements:
            if isinstance(achievement, dict):
                description = achievement.get('description', '').lower()
            else:
                description = str(achievement).lower()
            
            # Check if achievement keywords match job requirements
            if any(keyword in description for keyword in requirement_keywords):
                relevant_achievements.append(achievement)
        
        return relevant_achievements
    
    def _calculate_experience_relevance(self, user_profile: Dict[str, Any], position: str) -> float:
        """Calculate experience relevance score"""
        # Simple scoring based on position match
        user_title = user_profile.get('personal_info', {}).get('title', '').lower()
        target_position = position.lower()
        
        if user_title in target_position or target_position in user_title:
            return 0.9
        elif any(word in target_position for word in user_title.split()):
            return 0.7
        else:
            return 0.5
    
    def _calculate_confidence(self, matches: Dict[str, Any]) -> float:
        """Calculate overall match confidence"""
        skill_coverage = matches.get('skill_coverage', 0.0)
        experience_relevance = matches.get('experience_relevance', 0.0)
        
        # Weighted average
        confidence = (skill_coverage * 0.6) + (experience_relevance * 0.4)
        return min(confidence, 1.0)
    
    def _create_personalization_strategy(self, matches: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalization strategy based on matches"""
        strategy = {
            'primary_focus': '',
            'key_highlights': [],
            'unique_angle': '',
            'connection_points': [],
            'value_propositions': []
        }
        
        # Determine primary focus
        if matches['direct_matches']:
            strategy['primary_focus'] = f"Direct skill match: {', '.join(matches['direct_matches'][:3])}"
        elif matches['related_matches']:
            strategy['primary_focus'] = f"Related experience: {', '.join(matches['related_matches'][:3])}"
        else:
            strategy['primary_focus'] = "Transferable skills and experience"
        
        # Key highlights
        if matches['achievement_matches']:
            strategy['key_highlights'] = [match.get('description', str(match)) 
                                        for match in matches['achievement_matches'][:2]]
        
        # Unique angle
        if matches['unique_strengths']:
            strategy['unique_angle'] = f"Unique expertise in {', '.join(matches['unique_strengths'][:2])}"
        
        # Connection points
        strategy['connection_points'] = [
            f"Experience with {skill}" for skill in matches['direct_matches'][:3]
        ]
        
        # Value propositions
        strategy['value_propositions'] = [
            "Immediate contribution to technical challenges",
            "Proven track record of delivering results",
            "Strong problem-solving and analytical skills"
        ]
        
        return strategy
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get input schema for profile matcher tool"""
        return {
            'type': 'object',
            'properties': {
                'job_requirements': {
                    'type': 'string',
                    'description': 'Job description and requirements'
                },
                'position': {
                    'type': 'string',
                    'description': 'Job position title'
                }
            },
            'required': ['job_requirements']
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema for profile matcher tool"""
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'matches': {
                            'type': 'object',
                            'properties': {
                                'direct_matches': {'type': 'array', 'items': {'type': 'string'}},
                                'related_matches': {'type': 'array', 'items': {'type': 'string'}},
                                'missing_skills': {'type': 'array', 'items': {'type': 'string'}},
                                'unique_strengths': {'type': 'array', 'items': {'type': 'string'}},
                                'achievement_matches': {'type': 'array'},
                                'experience_relevance': {'type': 'number'},
                                'skill_coverage': {'type': 'number'}
                            }
                        },
                        'personalization_strategy': {'type': 'object'},
                        'match_confidence': {'type': 'number'}
                    }
                },
                'error_message': {'type': 'string'},
                'execution_time': {'type': 'number'},
                'metadata': {'type': 'object'}
            }
        } 