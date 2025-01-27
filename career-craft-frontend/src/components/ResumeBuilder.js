import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { resumeService } from '../services/resumeService';
import ResumeInput from './ResumeInput';
import ResumePreview from './ResumePreview';
import InitialChoiceStep from './InitialChoiceStep';

export default function ResumeBuilder() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState('choice'); // 'choice', 'upload', 'form', 'preview'
  const [resumeData, setResumeData] = useState({
    contact_info: {
      name: '',
      email: '',
      phone: '',
      location: ''
    },
    summary: '',
    experience: [],
    education: [],
    skills: [],
    projects: [],
    achievements: []
  });
  const [jobDescription, setJobDescription] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    if (id && id !== 'new') {
      loadResume();
      setActiveStep('form');
    }
  }, [id]);

  const loadResume = async () => {
    try {
      setLoading(true);
      const data = await resumeService.getResumeById(id);
      setResumeData(data);
      setJobDescription(data.target_job_description || '');
    } catch (error) {
      toast.error('Failed to load resume');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
  
    try {
      setLoading(true);
      const response = await resumeService.uploadResume(file, jobDescription);
  
      response.is_uploaded_resume = true;
      response.created_manually = false;
      
      // Fetch feedback and recommendations
      const [feedbackData, recommendationsData] = await Promise.all([
        resumeService.analyzeResume(response.id, jobDescription),
        resumeService.getJobRecommendations(response.id)
      ]);
      
      setResumeData(response);
      setFeedback(feedbackData);
      setRecommendations(recommendationsData);
      
      setActiveStep('preview');
      
      toast.success('Resume uploaded and analyzed successfully');
    } catch (error) {
      toast.error(error.message || 'Failed to upload resume');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const data = {
        ...resumeData,
        created_manually: true,
        is_uploaded_resume: false,
        title: resumeData.title || 'My Resume',
        summary: resumeData.summary || '',
        target_job_description: jobDescription,
        contact_info: {
          ...resumeData.contact_info,
          name: resumeData.contact_info.name || '',
          email: resumeData.contact_info.email || '',
          phone: resumeData.contact_info.phone || '',
          location: resumeData.contact_info.location || ''
        },
        education: (resumeData.education || []).map(edu => ({
          ...edu,
          institution: edu.institution || '',
          degree: edu.degree || '',
          field_of_study: edu.field_of_study || '',
          start_date: edu.start_date ? new Date(edu.start_date).toISOString() : null,
          end_date: edu.end_date ? new Date(edu.end_date).toISOString() : null,
          gpa: edu.gpa || null
        })),
        experience: (resumeData.experience || []).map(exp => ({
          ...exp,
          company: exp.company || '',
          position: exp.position || '',
          start_date: exp.start_date ? new Date(exp.start_date).toISOString() : null,
          end_date: exp.end_date ? new Date(exp.end_date).toISOString() : null,
          description: exp.description || '',
          highlights: exp.highlights || []
        })),
        skills: (resumeData.skills || []).map(skill => ({
          ...skill,
          name: skill.name || '',
          category: skill.category || 'Technical',
          proficiency_level: skill.proficiency_level || null
        })),
        projects: (resumeData.projects || []).map(project => ({
          ...project,
          title: project.title || '',
          description: project.description || '',
          technologies: project.technologies || [],
          url: project.url || null,
          start_date: project.start_date ? new Date(project.start_date).toISOString() : null,
          end_date: project.end_date ? new Date(project.end_date).toISOString() : null
        })),
        achievements: (resumeData.achievements || []).map(achievement => ({
          ...achievement,
          title: achievement.title || '',
          description: achievement.description || '',
          date: achievement.date ? new Date(achievement.date).toISOString() : null
        }))
      };

      let response;
      if (id && id !== 'new') {
        response = await resumeService.updateResume(id, data);
        toast.success('Resume updated successfully');
      } else {
        response = await resumeService.createResume(data);
        toast.success('Resume created successfully');
      }

      if (response.id) {
        try {
          const [feedbackData, recommendationsData] = await Promise.all([
            resumeService.analyzeResume(response.id, jobDescription),
            resumeService.getJobRecommendations(response.id)
          ]);
  
          response.created_manually = true;
          response.is_uploaded_resume = false;
  
          setFeedback(feedbackData);
          setRecommendations(recommendationsData);
          setResumeData(response);
          setActiveStep('preview');
        } catch (error) {
          console.error('Error getting resume feedback and recommendations:', error);
          
          response.created_manually = true;
          response.is_uploaded_resume = false;
          setResumeData(response);
          setActiveStep('preview');
          toast.error('Unable to generate resume analysis');
        }
      }
  
    } catch (error) {
      toast.error(error.message || 'Failed to save resume');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      setLoading(true);
      const blob = await resumeService.generateResume(resumeData.id, jobDescription);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${resumeData.contact_info.name}_resume.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Resume downloaded successfully');
    } catch (error) {
      toast.error('Failed to download resume');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">
            {id === 'new' ? 'Create New Resume' : 'Edit Resume'}
          </h1>
          <div className="flex space-x-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Cancel
            </button>
            {activeStep !== 'choice' && (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
              >
                {loading ? 'Saving...' : 'Save & Preview'}
              </button>
            )}
          </div>
        </div>

        {activeStep === 'choice' && (
          <InitialChoiceStep 
            onUploadClick={() => setActiveStep('upload')}
            onCreateClick={() => setActiveStep('form')}
          />
        )}

        {activeStep === 'upload' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Your Resume</h2>
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileUpload}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
            />
            <div className="mt-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Target Job Description</h2>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="w-full h-32 p-2 border rounded-md"
                placeholder="Paste the job description here..."
              />
            </div>
          </div>
        )}

        {activeStep === 'form' && (
          <div className="bg-white shadow rounded-lg">
            <div className="p-6">
              <div className="mb-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Target Job Description</h2>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="w-full h-32 p-2 border rounded-md"
                  placeholder="Paste the job description here..."
                />
              </div>
              <ResumeInput
                resumeData={resumeData}
                setResumeData={setResumeData}
              />
            </div>
          </div>
        )}

        {activeStep === 'preview' && (
          <ResumePreview
            resumeData={resumeData}
            feedback={feedback}
            recommendations={recommendations}
            onDownload={handleDownload}
            onEdit={() => setActiveStep('form')}
          />
        )}
      </div>
    </div>
  );
}