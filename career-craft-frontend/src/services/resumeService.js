import { authService } from './auth';
import { auth } from '../firebase';

const transformFormData = (formData) => {
  // Transform personal info to match backend schema
  const personal_info = {
    full_name: formData.personalInfo.fullName,
    email: formData.personalInfo.email,
    phone: formData.personalInfo.phone,
    location: formData.personalInfo.location
  };

  // Transform experience data
  const experience = formData.experience.map(exp => ({
    title: exp.title,
    company: exp.company,
    start_date: exp.startDate,
    end_date: exp.isCurrentPosition ? 'Present' : exp.endDate,
    description: exp.description,
    is_current: exp.isCurrentPosition
  }));

  // Transform education data
  const education = formData.education.map(edu => ({
    degree: edu.degree,
    institution: edu.institution,
    graduation_date: edu.graduationDate,
    gpa: edu.gpa,
    relevant_courses: edu.relevantCourses.map(course => ({
      course_name: course.courseName,
      skills_learned: course.skillsLearned
    }))
  }));

  // Transform skills from string to array if needed
  const skills = typeof formData.skills === 'string' 
    ? formData.skills.split(',').map(skill => skill.trim())
    : formData.skills;

  // Transform achievements
  const achievements = formData.achievements.map(achievement => ({
    title: achievement.title,
    description: achievement.description,
    date: achievement.date
  }));

  return {
    personal_info,
    summary: formData.summary,
    experience,
    education,
    skills,
    achievements,
    job_description: formData.jobDescription
  };
};

const handleFileUpload = async (file) => {
  const formData = new FormData();
  formData.append('resume', file);
  return formData;
};

export const generateResume = async (data) => {
  try {
    if (!auth.currentUser) {
      throw new Error('User not authenticated');
    }
    
    const token = await authService.getToken();
    if (!token) {
      throw new Error('No authentication token available');
    }

    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    
    // Prepare request data based on input method
    const requestData = data.inputMethod === 'form' 
      ? transformFormData(data.data)
      : await handleFileUpload(data.data);

    // Add job description to form data if file upload
    if (data.inputMethod === 'upload') {
      requestData.append('job_description', data.jobDescription);
    }

    const headers = {
      'Authorization': `Bearer ${token}`,
    };

    // Set appropriate Content-Type based on input method
    if (data.inputMethod === 'form') {
      headers['Content-Type'] = 'application/json';
    }
    // For FormData, browser will set the correct Content-Type with boundary

    const response = await fetch(`${API_URL}/generate-resume`, {
      method: 'POST',
      headers,
      body: data.inputMethod === 'form' 
        ? JSON.stringify(requestData)
        : requestData
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Server error response:', errorData);
      throw new Error(errorData.detail || 'Failed to generate resume');
    }

    const responseData = await response.json();
    
    return {
      pdf: responseData.pdf,
      feedback: responseData.feedback || {
        sections: [
          {
            title: "Resume Strength",
            score: responseData.score || 0,
            feedback: responseData.feedback_text || "Unable to generate detailed feedback."
          }
        ]
      },
      recommendations: responseData.job_recommendations || []
    };
  } catch (error) {
    console.error('Error generating resume:', error);
    throw error;
  }
};