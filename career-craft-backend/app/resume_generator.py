from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any

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
    
    def _add_header(self, data: Dict[str, Any]):
        name = self.document.add_paragraph()
        run = name.add_run(data['full_name'])
        run.bold = True
        run.font.size = Pt(16)
        name.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        contact = self.document.add_paragraph()
        contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
        contact_text = f"{data['email']} | {data['phone']} | {data['location']}"
        contact.add_run(contact_text).font.size = Pt(10)
    
    def _add_summary(self, summary: str):
        self.document.add_heading('Professional Summary', level=1)
        self.document.add_paragraph(summary)
    
    def _add_experience(self, experiences: list):
        self.document.add_heading('Work Experience', level=1)
        for exp in experiences:
            p = self.document.add_paragraph()
            p.add_run(f"{exp['title']} at {exp['company']}").bold = True
            p.add_run(f"\n{exp['start_date']} - {exp['end_date']}")
            
            if exp.get('responsibilities'):
                bullet_list = self.document.add_paragraph()
                for resp in exp['responsibilities']:
                    bullet_list.add_run(f"• {resp}\n")
    
    def _add_education(self, education: list):
        self.document.add_heading('Education', level=1)
        for edu in education:
            p = self.document.add_paragraph()
            p.add_run(f"{edu['degree']} in {edu['field']}").bold = True
            p.add_run(f"\n{edu['school']}")
            p.add_run(f"\n{edu['graduation_date']}")
    
    def generate(self, data: Dict[str, Any]) -> Document:
        self._add_header(data)
        self._add_summary(data['summary'])
        self._add_experience(data['experience'])
        self._add_education(data['education'])
        
        if data.get('skills'):
            self.document.add_heading('Skills', level=1)
            skills_para = self.document.add_paragraph()
            skills_para.add_run(', '.join(data['skills']))
        
        return self.document