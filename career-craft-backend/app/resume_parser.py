from typing import Dict, Any
import docx2txt
import PyPDF2
import re
import spacy
from pathlib import Path
import logging

class ResumeParser:
    def __init__(self):
        # Load English language model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("Downloading language model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            text = docx2txt.process(file_path)
            return text
        except Exception as e:
            logging.error(f"Error extracting text from DOCX: {e}")
            raise ValueError("Failed to process DOCX file")

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")
            raise ValueError("Failed to process PDF file")

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information using regex patterns."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        email = re.search(email_pattern, text)
        phone = re.search(phone_pattern, text)
        
        # Get the first few lines for name
        lines = text.split('\n')
        potential_name = next((line.strip() for line in lines if line.strip() 
                             and not re.search(email_pattern, line) 
                             and not re.search(phone_pattern, line)), "")

        return {
            "full_name": potential_name,
            "email": email.group(0) if email else None,
            "phone": phone.group(0) if phone else None,
            "location": None  # Location extraction requires more complex logic
        }

    def extract_sections(self, text: str) -> Dict[str, Any]:
        """Extract different sections of the resume."""
        # Basic section extraction
        sections = {
            "summary": "",
            "experience": [],
            "education": [],
            "skills": []
        }
        
        # Use NLP to identify sections
        doc = self.nlp(text)
        
        # Simple section identification based on common headers
        current_section = None
        current_content = []
        
        for line in text.split('\n'):
            line = line.strip()
            lower_line = line.lower()
            
            if any(keyword in lower_line for keyword in ['experience', 'work history']):
                current_section = 'experience'
                continue
            elif any(keyword in lower_line for keyword in ['education', 'academic']):
                current_section = 'education'
                continue
            elif any(keyword in lower_line for keyword in ['skills', 'technologies']):
                current_section = 'skills'
                continue
            elif any(keyword in lower_line for keyword in ['summary', 'objective']):
                current_section = 'summary'
                continue
                
            if current_section and line:
                current_content.append(line)
                
        # Process collected content
        if current_content:
            sections[current_section] = ' '.join(current_content)
        
        return sections

    def parse(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Main parsing function."""
        # Extract text based on file type
        if file_type == "application/pdf":
            text = self.extract_text_from_pdf(file_path)
        elif file_type in ["application/docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            text = self.extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file type")

        # Extract information
        contact_info = self.extract_contact_info(text)
        sections = self.extract_sections(text)

        # Combine all extracted information
        return {
            **contact_info,
            **sections
        }