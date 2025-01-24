from typing import List, Dict
from openai import OpenAI  # Updated import
from .schemas import ResumeFeedback, Resume, JobRecommendation
import json
import os
from dotenv import load_dotenv

load_dotenv()

class ResumeAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Use OpenAI client
        self.MAX_TOKENS = 2000
        self.MODEL = "gpt-3.5-turbo"
        
        # Load jobs data
        with open('data/jobs.json', 'r') as f:
            self.jobs_data = json.load(f)

    def _format_resume_for_analysis(self, resume: Resume) -> str:
        """Format resume data into a string for GPT analysis."""
        formatted_text = f"""
        Contact Information:
        {json.dumps(resume.contact_info, indent=2)}

        Summary:
        {resume.summary}

        Education:
        {self._format_education(resume.education)}

        Experience:
        {self._format_experience(resume.experience)}

        Skills:
        {self._format_skills(resume.skills)}
        """

        if resume.projects:
            formatted_text += f"\nProjects:\n{self._format_projects(resume.projects)}"

        if resume.achievements:
            formatted_text += f"\nAchievements:\n{self._format_achievements(resume.achievements)}"

        return formatted_text

    def analyze_resume(self, resume: Resume, job_description: str) -> ResumeFeedback:
        """Analyze resume against job description using GPT and provide feedback."""
        # Prepare resume data for GPT
        resume_text = self._format_resume_for_analysis(resume)
        
        # Create GPT prompt
        prompt = f"""
        Analyze the following resume for a job application. Provide specific feedback and suggestions for improvement.

        Job Description:
        {job_description}

        Resume:
        {resume_text}

        Please analyze the following aspects:
        1. Overall match with job requirements
        2. Missing key skills or qualifications
        3. Suggestions for improvement in each section
        4. Specific phrases or bullets that could be enhanced
        5. Additional certifications or skills that would be beneficial

        Provide structured feedback with specific actionable suggestions.
        """

        try:
            # Get GPT analysis - Updated method call
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer and career counselor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.MAX_TOKENS,
                temperature=0.7
            )
            
            # Parse GPT response - Updated access to response
            analysis = response.choices[0].message.content
            
            # Extract structured feedback
            feedback = self._parse_gpt_feedback(analysis)
            
            # Get job recommendations
            job_recommendations = self._get_job_recommendations(resume, job_description)
            
            # Combine feedback with job recommendations
            feedback.job_recommendations = job_recommendations
            
            return feedback

        except Exception as e:
            print(f"Error in GPT analysis: {str(e)}")
            # Return basic feedback if GPT fails
            return ResumeFeedback(
                overall_score=0.0,
                suggestions=["Error analyzing resume. Please try again."],
                missing_skills=[],
                improvement_areas={},
                job_recommendations=self._get_job_recommendations(resume, job_description)
            )

    def _parse_gpt_feedback(self, analysis: str) -> ResumeFeedback:
        """Parse GPT response into structured feedback."""
        # Use another GPT call to structure the feedback
        structuring_prompt = f"""
        Convert the following resume analysis into structured feedback with the following components:
        1. Overall score (0-100)
        2. List of specific suggestions
        3. List of missing skills
        4. Dictionary of improvement areas by section

        Analysis:
        {analysis}

        Return the response in the following JSON format:
        {{
            "overall_score": float,
            "suggestions": list[str],
            "missing_skills": list[str],
            "improvement_areas": dict[str, list[str]]
        }}
        """

        try:
            # Updated method call
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": "You are a JSON formatting assistant."},
                    {"role": "user", "content": structuring_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Updated access to response
            feedback_dict = json.loads(response.choices[0].message.content)
            
            return ResumeFeedback(
                overall_score=feedback_dict["overall_score"],
                suggestions=feedback_dict["suggestions"],
                missing_skills=feedback_dict["missing_skills"],
                improvement_areas=feedback_dict["improvement_areas"],
                job_recommendations=[]  # Will be filled later
            )

        except Exception as e:
            print(f"Error parsing GPT feedback: {str(e)}")
            return ResumeFeedback(
                overall_score=50.0,
                suggestions=["Unable to generate detailed feedback. Please try again."],
                missing_skills=[],
                improvement_areas={},
                job_recommendations=[]
            )

    def _get_job_recommendations(self, resume: Resume, job_description: str) -> List[JobRecommendation]:
        """Match resume against jobs database and return top 5 recommendations."""
        try:
            # Prepare input for skill matching
            resume_skills = set(skill.name.lower() for skill in resume.skills)
            resume_experience = " ".join([exp.description for exp in resume.experience])
            
            # Get GPT to extract key skills from job description
            target_skills_prompt = f"""
            Extract key technical skills, soft skills, and requirements from this job description:
            {job_description}
            Return only the list of skills, one per line.
            """
            
            # Updated method call
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": "Extract key skills and requirements."},
                    {"role": "user", "content": target_skills_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Updated access to response
            target_skills = set(
                skill.strip().lower() 
                for skill in response.choices[0].message.content.split('\n')
                if skill.strip()
            )
            
            # Rest of the method remains the same...
            
            # Score each job, sort, and get top recommendations
            job_scores = []
            for job in self.jobs_data:
                job_skills = set(skill.lower() for skill in job["requiredSkills"])
                
                # Calculate match score
                skill_match = len(resume_skills.intersection(job_skills)) / len(job_skills) if job_skills else 0
                target_match = len(target_skills.intersection(job_skills)) / len(target_skills) if target_skills else 0
                
                # Combine scores (weighted average)
                match_score = (skill_match * 0.7) + (target_match * 0.3)
                
                job_scores.append((job, match_score))
            
            # Sort and get top 5 recommendations
            job_scores.sort(key=lambda x: x[1], reverse=True)
            top_recommendations = []
            
            for job, score in job_scores[:5]:
                recommendation = JobRecommendation(
                    title=job["title"],
                    key_responsibilities=job["keyResponsibilities"],
                    required_skills=job["requiredSkills"],
                    category=job["category"],
                    match_score=round(score * 100, 2)
                )
                top_recommendations.append(recommendation)
            
            return top_recommendations

        except Exception as e:
            print(f"Error getting job recommendations: {str(e)}")
            return []

    def _format_education(self, education_list: List) -> str:
        """Format education entries for GPT analysis."""
        formatted = ""
        for edu in education_list:
            formatted += f"""
            Institution: {edu.institution}
            Degree: {edu.degree}
            Field: {edu.field_of_study}
            Duration: {edu.start_date.strftime('%B %Y')} - {edu.end_date.strftime('%B %Y') if edu.end_date else 'Present'}
            """
        return formatted

    def _format_experience(self, experience_list: List) -> str:
        """Format experience entries for GPT analysis."""
        formatted = ""
        for exp in experience_list:
            formatted += f"""
            Company: {exp.company}
            Position: {exp.position}
            Duration: {exp.start_date.strftime('%B %Y')} - {exp.end_date.strftime('%B %Y') if exp.end_date else 'Present'}
            Description: {exp.description}
            Highlights:
            """
            for highlight in exp.highlights:
                formatted += f"- {highlight}\n"
        return formatted

    def _format_skills(self, skills_list: List) -> str:
        """Format skills for GPT analysis."""
        skills_by_category = {}
        for skill in skills_list:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill.name)
        
        formatted = ""
        for category, skills in skills_by_category.items():
            formatted += f"\n{category}:\n- " + "\n- ".join(skills)
        return formatted

    def _format_projects(self, projects_list: List) -> str:
        """Format projects for GPT analysis."""
        formatted = ""
        for proj in projects_list:
            formatted += f"""
            Project: {proj.title}
            Description: {proj.description}
            Technologies: {', '.join(proj.technologies)}
            """
            if proj.url:
                formatted += f"URL: {proj.url}\n"
        return formatted

    def _format_achievements(self, achievements_list: List) -> str:
        """Format achievements for GPT analysis."""
        formatted = ""
        for achievement in achievements_list:
            formatted += f"""
            {achievement.title}
            {achievement.description}
            """
            if achievement.date:
                formatted += f"Date: {achievement.date.strftime('%B %Y')}\n"
        return formatted