from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any
import logging

class ResumeGenerator:
    def __init__(self):
        self.document = Document()
        self._setup_margins()
        
    def _setup_margins(self):
        sections = self.document.sections
        for section in sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)
    
    def _add_header(self, personal_info: Dict[str, Any]):
        try:
            # Add name
            name = self.document.add_paragraph()
            run = name.add_run(personal_info.get('full_name', ''))
            run.bold = True
            run.font.size = Pt(16)
            name.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Add contact info
            contact = self.document.add_paragraph()
            contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
            contact_info = [
                personal_info.get('email', ''),
                personal_info.get('phone', ''),
                personal_info.get('location', '')
            ]
            contact_text = ' | '.join(filter(None, contact_info))
            contact.add_run(contact_text).font.size = Pt(10)
        except Exception as e:
            logging.error(f"Error adding header: {str(e)}")
            raise ValueError("Failed to add header section")
    
    def _add_summary(self, summary: str):
        try:
            if summary:
                self.document.add_heading('Professional Summary', level=1)
                self.document.add_paragraph(summary)
        except Exception as e:
            logging.error(f"Error adding summary: {str(e)}")
            raise ValueError("Failed to add summary section")
    
    def _add_experience(self, experiences: list):
        try:
            if experiences:
                self.document.add_heading('Professional Experience', level=1)
                for exp in experiences:
                    p = self.document.add_paragraph()
                    p.add_run(f"{exp.get('title', '')} at {exp.get('company', '')}").bold = True
                    
                    # Handle dates
                    start_date = exp.get('start_date', '')
                    end_date = 'Present' if exp.get('is_current', False) else exp.get('end_date', '')
                    date_range = f"\n{start_date} - {end_date}"
                    p.add_run(date_range)
                    
                    # Handle description
                    if exp.get('description'):
                        desc_para = self.document.add_paragraph()
                        for bullet in exp['description'].split('\n'):
                            if bullet.strip():
                                desc_para.add_run(f"• {bullet.strip()}\n")
        except Exception as e:
            logging.error(f"Error adding experience: {str(e)}")
            raise ValueError("Failed to add experience section")
    
    def _add_education(self, education: list):
        try:
            if education:
                self.document.add_heading('Education', level=1)
                for edu in education:
                    p = self.document.add_paragraph()
                    degree_line = f"{edu.get('degree', '')} - {edu.get('institution', '')}"
                    p.add_run(degree_line).bold = True
                    
                    grad_date = edu.get('graduation_date', '')
                    if grad_date:
                        p.add_run(f"\nGraduation: {grad_date}")
                    
                    gpa = edu.get('gpa')
                    if gpa:
                        p.add_run(f"\nGPA: {gpa}")
                    
                    # Add relevant courses if available
                    courses = edu.get('relevant_courses', [])
                    if courses:
                        p.add_run("\nRelevant Coursework:")
                        for course in courses:
                            p.add_run(f"\n• {course.get('name', '')}")
                            if course.get('skills_learned'):
                                p.add_run(f" - {course.get('skills_learned')}")
        except Exception as e:
            logging.error(f"Error adding education: {str(e)}")
            raise ValueError("Failed to add education section")
    
    def _add_skills(self, skills: list):
        try:
            if skills:
                self.document.add_heading('Skills', level=1)
                skills_para = self.document.add_paragraph()
                skills_para.add_run(', '.join(skills))
        except Exception as e:
            logging.error(f"Error adding skills: {str(e)}")
            raise ValueError("Failed to add skills section")
    
    def _add_achievements(self, achievements: list):
        try:
            if achievements:
                self.document.add_heading('Achievements', level=1)
                for achievement in achievements:
                    p = self.document.add_paragraph()
                    p.add_run(f"{achievement.get('title', '')}").bold = True
                    if achievement.get('date'):
                        p.add_run(f" ({achievement.get('date')})")
                    if achievement.get('description'):
                        p.add_run(f"\n{achievement.get('description')}")
        except Exception as e:
            logging.error(f"Error adding achievements: {str(e)}")
            raise ValueError("Failed to add achievements section")
    
    def generate(self, data: Dict[str, Any]) -> tuple:
        logging.info(f"Starting resume generation with data: {data}")

        try:
            if not data.get('personal_info'):
                raise ValueError("Missing personal information")

            self._add_header(data.get('personal_info', {}))
            self._add_summary(data.get('summary', ''))
            self._add_experience(data.get('experience', []))
            self._add_education(data.get('education', []))
            self._add_skills(data.get('skills', []))
            self._add_achievements(data.get('achievements', []))

            feedback = "Resume generated successfully. Consider tailoring your summary to the job description."  # Example feedback
            return self.document, feedback  # Now returning both document and feedback

        except Exception as e:
            logging.error(f"Detailed error generating resume: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to generate resume: {str(e)}")
