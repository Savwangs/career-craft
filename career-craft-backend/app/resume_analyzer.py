from typing import Dict, List
from openai import OpenAI
import json
from .utils import client

class ResumeAnalyzer:
    def __init__(self):
        self.client = client

    def analyze_resume(self, resume_content: Dict, job_description: str) -> Dict:
        """
        Analyzes a resume against a job description and provides improvement suggestions.
        """
        logging.info("Starting resume analysis")
    
        try:
            # Validate inputs
            if not resume_content:
                raise ValueError("Resume content is missing")
            if not job_description:
                raise ValueError("Job description is missing")
                
            # Create the analysis prompt
            prompt = self._create_analysis_prompt(resume_content, job_description)
        
            # Get GPT analysis
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=[
                    {"role": "system", "content": """You are an expert resume analyzer. 
                    Provide specific, actionable feedback to improve resumes for target positions.
                    Focus on keyword alignment, achievement highlighting, and professional presentation."""},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
        
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            logging.error(f"Error analyzing resume: {str(e)}", exc_info=True)
            raise Exception(f"Resume analysis failed: {str(e)}")

    def _create_analysis_prompt(self, resume_content: Dict, job_description: str) -> str:
        """Creates a detailed prompt for GPT analysis."""
        return f"""Analyze the following resume against the job description and provide feedback in JSON format.
        
        RESUME:
        {json.dumps(resume_content, indent=2)}
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide analysis in the following JSON structure:
        {{
            "keyword_alignment": {{
                "missing_keywords": [],
                "suggestions": []
            }},
            "achievement_improvements": {{
                "section": "experience/education",
                "current": "original text",
                "suggested": "improved text with metrics"
            }},
            "skills_feedback": {{
                "relevant_skills": [],
                "missing_skills": [],
                "suggestions": []
            }},
            "overall_recommendations": []
        }}"""

    def suggest_job_titles(self, resume_content: Dict) -> List[str]:
        """
        Suggests relevant job titles based on the resume content.
        
        Args:
            resume_content: Dictionary containing resume sections
        
        Returns:
            List of suggested job titles
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert career counselor. Suggest relevant job titles based on the candidate's experience and skills."},
                    {"role": "user", "content": f"""Based on this resume content and the job description, suggest 5 relevant job titles that this candidate should consider applying for:
                    
                    {json.dumps(resume_content, indent=2)}
                    
                    Return ONLY a JSON array of job titles."""}
                ],
                response_format={ "type": "json_object" }
            )
            
            return json.loads(response.choices[0].message.content)["job_titles"]
            
        except Exception as e:
            raise Exception(f"Error suggesting job titles: {str(e)}")