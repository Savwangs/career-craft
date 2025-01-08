import React, { useState } from 'react';
import ResumeInput from './ResumeInput';
import ResumePreview from './ResumePreview';
import { apiService } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ResumeBuilder = () => {
    const navigate = useNavigate();
    const { currentUser } = useAuth();
    const [resumeData, setResumeData] = useState(null);
    const [jobDescription, setJobDescription] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleResumeSubmit = async (data) => {
        try {
            setIsLoading(true);
            setError(null);
            let response;
            
            if (data.inputMethod === 'form') {
                response = await apiService.createResume(currentUser.token, {
                    resumeData: data.data,
                    jobDescription: data.jobDescription
                });
            } else {
                const formData = new FormData();
                formData.append('resume', data.data);
                formData.append('jobDescription', data.jobDescription);
                
                response = await apiService.createResume(currentUser.token, formData);
            }

            setResumeData(response.content);
            setJobDescription(data.jobDescription);

            if (response.id) {
                navigate('/dashboard');
            }
        } catch (error) {
            console.error('Error creating resume:', error);
            setError('Failed to process resume. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                    <ResumeInput onSubmit={handleResumeSubmit} />
                    {error && (
                        <div className="mt-4 p-4 bg-red-50 text-red-500 rounded-md">
                            {error}
                        </div>
                    )}
                </div>
                
                {(resumeData && jobDescription) && (
                    <div className="lg:sticky lg:top-8">
                        <ResumePreview 
                            resumeContent={resumeData}
                            jobDescription={jobDescription}
                        />
                    </div>
                )}
            </div>
            
            {isLoading && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
                </div>
            )}
        </div>
    );
};

export default ResumeBuilder;