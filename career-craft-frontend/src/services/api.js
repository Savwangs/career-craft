const API_URL = process.env.REACT_APP_API_URL;

export const apiService = {
  async getResumes(token) {
    const response = await fetch(`${API_URL}/resumes/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) throw new Error('Failed to fetch resumes');
    return response.json();
  },

  async createResume(token, data) {
    console.log('Sending data to API:', data); // Debug log
    
    const response = await fetch(`${API_URL}/generate-resume`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        full_name: data.resumeData.personalInfo.fullName,
        email: data.resumeData.personalInfo.email,
        phone: data.resumeData.personalInfo.phone,
        location: data.resumeData.personalInfo.location,
        summary: data.resumeData.summary,
        experience: data.resumeData.experience.map(exp => ({
          title: exp.title,
          company: exp.company,
          start_date: exp.startDate,
          end_date: exp.endDate,
          responsibilities: [exp.description]
        })),
        education: data.resumeData.education.map(edu => ({
          degree: edu.degree,
          field: edu.degree, // You might want to add a field property to your form
          school: edu.institution,
          graduation_date: edu.graduationDate
        })),
        skills: data.resumeData.skills.split(',').map(skill => skill.trim())
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error:', errorText); // Debug log
      throw new Error(errorText);
    }
    
    return response;
  },

  async updateResume(token, id, content) {
    const response = await fetch(`${API_URL}/resumes/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content })
    });
    if (!response.ok) throw new Error('Failed to update resume');
    return response.json();
  },

  async deleteResume(token, id) {
    const response = await fetch(`${API_URL}/resumes/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) throw new Error('Failed to delete resume');
    return response;
  },
  
  async getJobRecommendations(token, resumeContent, jobDescription) {
    const response = await fetch(`${API_URL}/resume/recommendations`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ resumeContent, jobDescription })
    });
    if (!response.ok) throw new Error('Failed to get recommendations');
    return response.json();
  }
};

