import React, { useState } from 'react';
import ResumeInput from './ResumeInput';
import ResumePreview from './ResumePreview';
import { apiService } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getAuth } from "firebase/auth";

const ResumeBuilder = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [resumeData, setResumeData] = useState(null);
    const [jobDescription, setJobDescription] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [feedback, setFeedback] = useState(null);
    const [recommendations, setRecommendations] = useState(null);

    const handleResumeSubmit = async (data) => {
        console.log('Data being submitted:', data);
    
        const auth = getAuth();
        const currentUser = auth.currentUser;
    
        if (!currentUser) {
            setError('Authentication error. Please log in again.');
            return;
        }

        const token = await currentUser.getIdToken();
    
        try {
            setIsLoading(true);
            setError(null);
    
            const response = await apiService.createResume(token, {
                inputMethod: data.inputMethod,
                data: data.data,
                jobDescription: data.jobDescription
            });
    
            // Update state with all response data
            if (response.content) {
                setResumeData(response.content);
            }
            setJobDescription(data.jobDescription);
            setFeedback(response.feedback);
            setRecommendations(response.recommendations);
    
        } catch (error) {
            console.error('Error creating resume:', error);
            setError(error.message || 'Failed to process resume. Please try again.');
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
                    {feedback && (
                        <div className="mt-4 p-4 bg-blue-50 text-blue-700 rounded-md">
                            <h3 className="font-bold mb-2">Feedback:</h3>
                            <p>{feedback}</p>
                        </div>
                    )}
                    {recommendations && recommendations.length > 0 && (
                        <div className="mt-4 p-4 bg-green-50 text-green-700 rounded-md">
                            <h3 className="font-bold mb-2">Recommendations:</h3>
                            <ul className="list-disc pl-4">
                                {recommendations.map((rec, index) => (
                                    <li key={index}>{rec}</li>
                                ))}
                            </ul>
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