import axios from 'axios';
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
    console.log('Preparing data for API submission:', data);

    if (data.inputMethod === 'form') {
        if (!data.data) {
            throw new Error('Missing resume data for form input');
        }

        // Transform form data
        const transformedEducation = data.data.education.map(edu => ({
            degree: edu.degree,
            institution: edu.institution,
            graduation_date: edu.graduationDate,
            gpa: edu.gpa || '',
            relevant_courses: edu.relevantCourses.map(course => ({
                name: course.courseName,
                skills: course.skillsLearned
            }))
        }));

        const transformedExperience = data.data.experience.map(exp => ({
            title: exp.title,
            company: exp.company,
            start_date: exp.startDate,
            end_date: exp.isCurrentPosition ? 'Present' : exp.endDate,
            is_current: exp.isCurrentPosition,
            description: exp.description
        }));

        const transformedAchievements = data.data.achievements.map(achievement => ({
            title: achievement.title,
            date: achievement.date,
            description: achievement.description
        }));

        const requestData = {
            personal_info: {
                full_name: data.data.personalInfo.fullName,
                email: data.data.personalInfo.email,
                phone: data.data.personalInfo.phone,
                location: data.data.personalInfo.location
            },
            summary: data.data.summary,
            experience: transformedExperience,
            education: transformedEducation,
            skills: Array.isArray(data.data.skills) ? data.data.skills : data.data.skills.split(',').map(skill => skill.trim()),
            achievements: transformedAchievements,
            job_description: data.jobDescription
        };

        try {
            console.log('Sending form request data:', requestData);

            const response = await fetch(`${API_URL}/generate-resume`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            const responseText = await response.text();
            console.log('Raw API Response:', responseText);

            if (!response.ok) {
                throw new Error(`API Error (${response.status}): ${responseText}`);
            }

            let responseData;
            try {
                responseData = JSON.parse(responseText);
            } catch (e) {
                console.error('Failed to parse API response:', e);
                throw new Error('Invalid response format from server');
            }

            const result = {
              feedback: responseData.feedback || 'No feedback available',
              recommendations: responseData.recommendations || [],
              content: null,
              contentType: null
            };

            
            if (responseData.pdf && responseData.pdf.length > 0) {
              try {
                  const pdfBlob = await fetch(`data:application/pdf;base64,${responseData.pdf}`).then(r => r.blob());
                  result.content = URL.createObjectURL(pdfBlob);
                  result.contentType = 'application/pdf';
              } catch (e) {
                  console.error('Error processing PDF content:', e);
              }
            } else {
                console.log('No PDF content received from server');
            }            

            return result;
        } catch (error) {
            console.error('Resume creation error:', error);
            throw new Error(error.message || 'Failed to create resume');
        }
    } else if (data.inputMethod === 'upload') {
        const formData = new FormData();
        formData.append('file', data.data);
        formData.append('job_description', data.jobDescription);

        try {
            console.log('Uploading file:', formData);

            const response = await fetch(`${API_URL}/upload-resume`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Upload API Error:', errorText);
                throw new Error(`Upload failed: ${errorText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Resume upload error:', error);
            throw new Error(error.message || 'Failed to upload resume');
        }
    } else {
        console.error('Received input method:', data.inputMethod);
        throw new Error('Invalid input method');
      }
  },

  async uploadResume(token, file, jobDescription) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);

    try {
      const response = await fetch(`${API_URL}/upload-resume`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Upload API Error:', errorText);
        throw new Error(`Upload failed: ${errorText}`);
      }

      return response.json();
    } catch (error) {
      console.error('Resume upload error:', error);
      throw new Error(error.message || 'Failed to upload resume');
    }
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
  
  async getJobRecommendations(token, resumeId) {
    const response = await fetch(`${API_URL}/suggest-jobs/${resumeId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to get recommendations: ${errorText}`);
    }
    return response.json();
  },

  async analyzeResume(token, resumeId, jobDescription) {
    const response = await fetch(`${API_URL}/analyze-resume`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        resume_id: resumeId,
        job_description: jobDescription
      })
    });
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to analyze resume: ${errorText}`);
    }
    return response.json();
  }
};