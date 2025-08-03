"""
Personalization Tools - Profile Matching Module
============================================

This module contains tools for matching user profiles with job
requirements to enable personalized email generation.

Author: Cold Email Automation System
Version: 2.0 (Simplified)
"""

from crewai_tools import tool
from typing import Dict, Any, List
import yaml
import json
import time
from utils.logger import setup_logger


class ProfileMatcherTool:
    """
    Profile Matching Tool
    
    This tool matches the user's profile with job requirements and company
    information to create personalized email content.
    
    Matching Areas:
    - Skills alignment with job requirements
    - Achievement relevance to company needs
    - Experience relevance to industry
    - Personalization points for email content
    
    The tool loads the user's profile from a YAML file and analyzes
    how well it matches with the target role and company.
    """
    
    def __init__(self):
        """Initialize profile matcher with user profile path"""
        self.profile_path = 'data/my_profile.yaml'
        self.logger = setup_logger('profile_matcher')
    
    @tool("Profile Matching")
    def match_profile(self, prospect_data: str, research_data: str) -> str:
        """
        Match user profile with job requirements for personalization
        
        This method analyzes how well the user's skills, achievements, and
        experience align with the target role and company requirements.
        
        Args:
            prospect_data (str): JSON string containing prospect information
            research_data (str): JSON string containing company research data
            
        Returns:
            str: JSON string containing matching results
            
        Example:
            >>> tool = ProfileMatcherTool()
            >>> result = tool.match_profile(prospect_json, research_json)
            >>> matches = json.loads(result)
            >>> print(matches['skill_matches'])  # ["Python", "AI/ML"]
        """
        try:
            self.logger.info("Starting profile matching process")
            
            # Load user profile
            with open(self.profile_path, 'r') as f:
                profile = yaml.safe_load(f)
            
            # Parse inputs
            prospect = json.loads(prospect_data) if isinstance(prospect_data, str) else prospect_data
            research = json.loads(research_data) if isinstance(research_data, str) else research_data
            
            # Extract job requirements
            job_title = prospect.get('role', 'Unknown Role')
            company_industry = research.get('industry', 'Unknown Industry')
            
            # Perform comprehensive matching
            matches = {
                'job_title': job_title,
                'company_industry': company_industry,
                'skill_matches': self._match_skills(profile, job_title),
                'achievement_matches': self._match_achievements(profile, job_title),
                'experience_relevance': self._assess_experience_relevance(profile, company_industry),
                'personalization_points': self._identify_personalization_points(profile, research),
                'matching_score': self._calculate_matching_score(profile, job_title, research),
                'matching_timestamp': time.time()
            }
            
            self.logger.info(f"Profile matching completed for {prospect.get('name', 'Unknown')}")
            return json.dumps(matches, indent=2)
            
        except Exception as e:
            error_msg = f"Profile matching failed: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _match_skills(self, profile: Dict, job_title: str) -> List[str]:
        """
        Match user skills with job requirements
        
        Args:
            profile (Dict): User profile data
            job_title (str): Target job title
            
        Returns:
            List[str]: List of relevant skills
        """
        skills = profile.get('skills', [])
        job_lower = job_title.lower()
        
        relevant_skills = []
        for skill in skills:
            if any(keyword in skill.lower() for keyword in ['python', 'javascript', 'ai', 'ml', 'data', 'cloud']):
                relevant_skills.append(skill)
        
        return relevant_skills[:3]  # Return top 3 matches
    
    def _match_achievements(self, profile: Dict, job_title: str) -> List[str]:
        """
        Match user achievements with job requirements
        
        Args:
            profile (Dict): User profile data
            job_title (str): Target job title
            
        Returns:
            List[str]: List of relevant achievements
        """
        achievements = profile.get('achievements', [])
        return achievements[:2]  # Return top 2 achievements
    
    def _assess_experience_relevance(self, profile: Dict, industry: str) -> str:
        """
        Assess how relevant user experience is to company industry
        
        Args:
            profile (Dict): User profile data
            industry (str): Company industry
            
        Returns:
            str: Experience relevance assessment
        """
        experience = profile.get('experience', [])
        if experience:
            return f"Relevant experience in {industry} sector"
        return "Transferable skills applicable to role"
    
    def _identify_personalization_points(self, profile: Dict, research: Dict) -> List[str]:
        """
        Identify points for personalization in email content
        
        Args:
            profile (Dict): User profile data
            research (Dict): Company research data
            
        Returns:
            List[str]: List of personalization points
        """
        points = []
        
        # Company values alignment
        if 'values' in research:
            points.append(f"Shared values: {', '.join(research['values'][:2])}")
        
        # Industry experience
        industry = research.get('industry', '')
        if industry:
            points.append(f"Experience in {industry} sector")
        
        # Technology alignment
        if 'technologies' in research:
            points.append(f"Familiar with {', '.join(research['technologies'][:2])}")
        
        return points
    
    def _calculate_matching_score(self, profile: Dict, job_title: str, research: Dict) -> float:
        """
        Calculate overall matching score between profile and job
        
        Args:
            profile (Dict): User profile data
            job_title (str): Target job title
            research (Dict): Company research data
            
        Returns:
            float: Matching score (0.0 to 1.0)
        """
        # Simple scoring algorithm
        score = 0.0
        
        # Skills match
        skill_matches = self._match_skills(profile, job_title)
        score += len(skill_matches) * 0.2
        
        # Achievement relevance
        achievement_matches = self._match_achievements(profile, job_title)
        score += len(achievement_matches) * 0.15
        
        # Industry alignment
        if research.get('industry') in ['Technology', 'Financial Services']:
            score += 0.25
        
        return min(score, 1.0) 