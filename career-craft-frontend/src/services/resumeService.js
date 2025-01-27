import { getAuthToken } from './auth';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const handleResponse = async (response) => {
  const contentType = response.headers.get("content-type");
  if (!response.ok) {
    if (contentType && contentType.indexOf("application/json") !== -1) {
      const error = await response.json();
      throw new Error(error.detail || 'An error occurred');
    } else {
      const text = await response.text();
      throw new Error(text || 'An error occurred');
    }
  }
  
  if (contentType && contentType.indexOf("application/json") !== -1) {
    return response.json();
  }
  return response;
};

const getHeaders = async (includeContentType = true) => {
  const token = await getAuthToken();
  const headers = {
    'Authorization': `Bearer ${token}`,
  };
  
  if (includeContentType) {
    headers['Content-Type'] = 'application/json';
  }
  
  return headers;
};

export const resumeService = {
  async getResumes() {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_URL}/api/resumes`, { headers });
      return handleResponse(response);
    } catch (error) {
      console.error('Get resumes error:', error);
      throw error;
    }
  },

  async getResume(id) {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_URL}/api/resumes/${id}`, { headers });
      return handleResponse(response);
    } catch (error) {
      console.error('Get resume error:', error);
      throw error;
    }
  },

  async createResume(data) {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_URL}/api/resumes`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          ...data,
          created_manually: true,
          is_uploaded_resume: false
        }),
      });
      return handleResponse(response);
    } catch (error) {
      console.error('Create resume error:', error);
      throw error;
    }
  },

  async updateResume(id, data) {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_URL}/api/resumes/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(data),
      });
      return handleResponse(response);
    } catch (error) {
      console.error('Update resume error:', error);
      throw error;
    }
  },

  async deleteResume(id) {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_URL}/api/resumes/${id}`, {
        method: 'DELETE',
        headers,
      });
      return handleResponse(response);
    } catch (error) {
      console.error('Delete resume error:', error);
      throw error;
    }
  },

  async analyzeResume(id, jobDescription) {
    try {
      const response = await fetch(`${API_URL}/api/resumes/${id}/analyze`, {
        method: 'POST',
        headers: await getHeaders(),
        body: JSON.stringify({ job_description: jobDescription })
      });
      const data = await handleResponse(response);
      console.log('Resume Analysis:', data);  // Add this line
      return data;
    } catch (error) {
      console.error('Analyze resume error:', error);
      throw error;
    }
  },

  async generateResume(id, jobDescription) {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_URL}/api/resumes/${id}/generate`, {
        method: 'POST', // Change to POST
        headers,
        body: JSON.stringify({ job_description: jobDescription }) // Send job description
      });
      return await response.blob(); // Return blob for download
    } catch (error) {
      console.error('Generate resume error:', error);
      throw error;
    }
  },

  async uploadResume(file, jobDescription) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('created_manually', false);
      formData.append('is_uploaded_resume', true);
      formData.append('resume_type', 'Uploaded Resume');
      formData.append('job_description', jobDescription);
  
      const headers = await getHeaders(false); 
      delete headers['Content-Type']; 
      
      const response = await fetch(`${API_URL}/api/resumes/upload`, {
        method: 'POST',
        headers,
        body: formData,
      });
      
      return handleResponse(response);
    } catch (error) {
      console.error('Upload resume error:', error);
      throw error;
    }
  },

  async getJobRecommendations(resumeId) {
    try {
      const response = await fetch(`${API_URL}/api/jobs/recommendations?resume_id=${resumeId}`, { 
        method: 'GET',
        headers: await getHeaders() 
      });
      const data = await handleResponse(response);
      console.log('Job Recommendations:', data);  // Add this line
      return data;
    } catch (error) {
      console.error('Get job recommendations error:', error);
      throw error;
    }
  }
};