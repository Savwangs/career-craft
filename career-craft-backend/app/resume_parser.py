from typing import Dict, Optional
import docx2txt
import PyPDF2
import re
import spacy
from dateutil import parser as date_parser
import os
from .schemas import ResumeCreate
from datetime import datetime

class ResumeParser:
    def __init__(self):
        # Load SpaCy model for NER
        self.nlp = spacy.load("en_core_web_sm")
        
        # Common section headers in resumes
        self.sections = {
            'education': r'education|academic|qualification',
            'experience': r'experience|employment|work history|work experience',
            'skills': r'skills|technical skills|competencies',
            'projects': r'projects|personal projects',
            'achievements': r'achievements|accomplishments|honors'
        }
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file."""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text content from DOCX file."""
        return docx2txt.process(file_path)

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information using regex and SpaCy NER."""
        doc = self.nlp(text[:1000])  # Process first 1000 chars for efficiency
        
        contact_info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()

        # Extract phone
        phone_pattern = r'\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()

        # Extract location using SpaCy NER
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC']:
                contact_info['location'] = ent.text
                break

        return contact_info

    def extract_education(self, text: str) -> list:
        """Extract education information."""
        education_section = self._extract_section(text, self.sections['education'])
        if not education_section:
            return []

        education_list = []
        # Split into entries based on common degree keywords
        degree_patterns = r'(?:Bachelor|Master|PhD|B\.|M\.|Ph\.D|Associate)'
        entries = re.split(degree_patterns, education_section)
        
        for entry in entries[1:]:  # Skip first split as it's usually empty
            try:
                # Extract degree
                degree_match = re.search(degree_patterns, entry)
                degree = degree_match.group() if degree_match else ""
                
                # Extract institution
                institution = ""
                lines = entry.split('\n')
                for line in lines:
                    if re.search(r'University|College|Institute', line):
                        institution = line.strip()
                        break

                # Extract dates
                dates = self._extract_dates(entry)
                
                if degree and institution:
                    education_list.append({
                        "institution": institution,
                        "degree": degree,
                        "field_of_study": "",  # Would need more complex parsing
                        "start_date": dates.get('start_date'),
                        "end_date": dates.get('end_date'),
                        "gpa": self._extract_gpa(entry)
                    })
            except Exception as e:
                print(f"Error parsing education entry: {str(e)}")
                continue

        return education_list

    def extract_experience(self, text: str) -> list:
        """Extract work experience information."""
        experience_section = self._extract_section(text, self.sections['experience'])
        if not experience_section:
            return []

        experience_list = []
        # Split into entries based on company/position patterns
        entries = re.split(r'\n(?=[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*(?:Ltd\.?|Inc\.?|Corp\.?)?)', experience_section)
        
        for entry in entries:
            try:
                lines = entry.split('\n')
                if not lines:
                    continue

                # Extract company and position
                company = lines[0].strip()
                position = lines[1].strip() if len(lines) > 1 else ""

                # Extract dates
                dates = self._extract_dates(entry)

                # Extract description and highlights
                description = ""
                highlights = []
                for line in lines[2:]:
                    line = line.strip()
                    if line.startswith(('•', '-', '●')):
                        highlights.append(line.lstrip('•- ●'))
                    else:
                        description += line + " "

                if company and position:
                    experience_list.append({
                        "company": company,
                        "position": position,
                        "start_date": dates.get('start_date'),
                        "end_date": dates.get('end_date'),
                        "description": description.strip(),
                        "highlights": highlights
                    })
            except Exception as e:
                print(f"Error parsing experience entry: {str(e)}")
                continue

        return experience_list

    def extract_skills(self, text: str) -> list:
        """Extract skills information."""
        skills_section = self._extract_section(text, self.sections['skills'])
        if not skills_section:
            return []

        skills_list = []
        # Split by common delimiters
        skills_text = re.sub(r'[•\-,|]', '\n', skills_section)
        
        for skill in skills_text.split('\n'):
            skill = skill.strip()
            if skill and len(skill) > 1:
                skills_list.append({
                    "name": skill,
                    "category": "Technical",  # Default category
                    "proficiency_level": None
                })

        return skills_list

    def _extract_section(self, text: str, section_pattern: str) -> Optional[str]:
        """Extract a section from the resume text."""
        pattern = re.compile(section_pattern, re.IGNORECASE)
        matches = list(pattern.finditer(text))
        
        if not matches:
            return None

        start_idx = matches[0].start()
        
        # Find the start of the next section
        next_section_start = len(text)
        for section_pattern in self.sections.values():
            pattern = re.compile(section_pattern, re.IGNORECASE)
            matches = list(pattern.finditer(text[start_idx + 1:]))
            if matches:
                next_start = start_idx + 1 + matches[0].start()
                next_section_start = min(next_section_start, next_start)

        return text[start_idx:next_section_start].strip()

    def _extract_dates(self, text: str) -> Dict[str, Optional[datetime]]:
        """Extract start and end dates from text."""

        # Common date formats in resumes
        date_patterns = [
            r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
            r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|'
            r'Dec(?:ember)?)[,\s]+\d{4}',
            r'\d{1,2}/\d{4}',
            r'\d{4}'
        ]
    
        dates = []
        for pattern in date_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    date = date_parser.parse(match.group())
                    dates.append(date)
                except:
                    continue

        dates.sort()
    
        # If no dates found, use current date as default
        if not dates:
            default_date = datetime.now().replace(month=1, day=1)
            return {
                'start_date': default_date,
                'end_date': None
            }

        return {
            'start_date': dates[0],
            'end_date': dates[-1] if len(dates) > 1 else None
        }

    def _extract_gpa(self, text: str) -> Optional[str]:
        """Extract GPA from text."""
        gpa_pattern = r'GPA:\s*(\d+\.\d+)|(\d+\.\d+)\s*GPA'
        match = re.search(gpa_pattern, text)
        return match.group(1) if match else None

    def parse_resume(self, file_path: str) -> ResumeCreate:
        try:
            """Main method to parse resume file and return structured data."""
            # Determine file type and extract text
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension == '.pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                text = self.extract_text_from_docx(file_path)
            else:
                raise ValueError("Unsupported file format")

            # Extract all components
            contact_info = self.extract_contact_info(text)
            education = self.extract_education(text)
            experience = self.extract_experience(text)
            skills = self.extract_skills(text)

            # Create ResumeCreate object
            resume_data = ResumeCreate(
                title=f"Uploaded Resume - {os.path.basename(file_path)}",
                summary=self._generate_summary(text),  # New method to generate summary
                contact_info=contact_info,
                created_manually=False,  # Mark as uploaded
                is_uploaded_resume=True,
                target_job_description="",
                education=education,
                experience=experience,
                skills=skills,
                projects=[],
                achievements=[]
            )

            return resume_data
        except ValueError as ve:
            # Handle unsupported file formats
            print(f"ValueError: {ve}")
            raise

    def _generate_summary(self, text: str) -> str:
        """Generate a professional summary using extracted text."""
        # Use NLP to create a concise summary
        doc = self.nlp(text[:2000])  # Process first 2000 chars
        summary_sentences = [sent.text for sent in doc.sents][:3]
        return " ".join(summary_sentences)
