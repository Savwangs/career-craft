# tests/test_resume_generator.py
import pytest
from app.resume_generator import ResumeGenerator

def test_resume_generation():
    test_data = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "123-456-7890",
        "location": "New York, NY",
        "summary": "Experienced software engineer...",
        "experience": [{
            "title": "Senior Developer",
            "company": "Tech Corp",
            "start_date": "2020",
            "end_date": "Present",
            "responsibilities": ["Led team of 5 developers", "Implemented CI/CD pipeline"]
        }],
        "education": [{
            "degree": "Bachelor's",
            "field": "Computer Science",
            "school": "University of Technology",
            "graduation_date": "2019"
        }],
        "skills": ["Python", "JavaScript", "SQL"]
    }
    
    generator = ResumeGenerator()
    doc = generator.generate(test_data)
    
    # Basic validation
    assert doc is not None
    assert len(doc.paragraphs) > 0