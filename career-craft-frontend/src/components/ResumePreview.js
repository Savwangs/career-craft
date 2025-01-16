import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { apiService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { generateResume } from '../services/resumeService';

const ResumePreview = ({ resumeContent, setResumeContent, jobDescription }) => {
    const [feedback, setFeedback] = useState(null);
    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { currentUser } = useAuth();

    useEffect(() => {
        const generateResumePreview = async () => {
            if (!resumeContent || !jobDescription) {
                setError('Both resume and job description are required');
                setLoading(false);
                return;
            }
        
            try {
                setLoading(true);
                setError(null);
                const result = await generateResume({
                    inputMethod: 'form',
                    data: resumeContent,
                    jobDescription: jobDescription
                });
                
                setFeedback(result.feedback);
                setRecommendations(result.recommendations);
                
                if (result.pdf) {
                    const pdfBlob = new Blob(
                        [Uint8Array.from(atob(result.pdf), c => c.charCodeAt(0))],
                        { type: 'application/pdf' }
                    );
                    setResumeContent({
                        contentType: 'application/pdf',
                        content: URL.createObjectURL(pdfBlob)
                    });
                }
            } catch (err) {
                console.error('Resume generation error:', err);
                setError(err.message || 'Failed to generate resume preview');
                setFeedback(null);
                setRecommendations(null);
            } finally {
                setLoading(false);
            }
        };
    
        generateResumePreview();
    }, [resumeContent, jobDescription]);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 text-red-500 bg-red-50 rounded-md">
                {error}
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Resume Preview Section */}
            <Card>
                <CardHeader>
                    <CardTitle>Resume Preview</CardTitle>
                </CardHeader>
                <CardContent>
                    {resumeContent.contentType === 'application/pdf' ? (
                        <iframe
                            src={resumeContent.content}
                            className="w-full h-[800px] border-0"
                            title="Resume Preview"
                        />
                    ) : (
                        <div className="prose max-w-none">
                            {resumeContent}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Feedback Section */}
            <Card>
                <CardHeader>
                    <CardTitle>AI Feedback</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {feedback?.sections?.map((section, index) => (
                            <div key={index} className="border-l-4 border-blue-500 pl-4">
                                <h3 className="font-semibold text-lg">{section.title}</h3>
                                <p className="text-gray-700">{section.feedback}</p>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Job Recommendations Section */}
            <Card>
                <CardHeader>
                    <CardTitle>Recommended Jobs</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-6">
                        {recommendations?.jobs?.map((job, index) => (
                            <div key={index} className="border-b last:border-b-0 pb-4">
                                <h3 className="font-semibold text-xl text-blue-600">{job.title}</h3>
                                <p className="text-gray-600 text-sm mt-1">Category: {job.category}</p>
                                <div className="mt-3">
                                    <h4 className="font-medium">Key Responsibilities:</h4>
                                    <ul className="list-disc pl-5 mt-2">
                                        {job.keyResponsibilities.map((resp, idx) => (
                                            <li key={idx} className="text-gray-700">{resp}</li>
                                        ))}
                                    </ul>
                                </div>
                                <div className="mt-3">
                                    <h4 className="font-medium">Required Skills:</h4>
                                    <ul className="list-disc pl-5 mt-2">
                                        {job.keySkills?.map((skill, idx) => (
                                            <li key={idx} className="text-gray-700">{skill}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default ResumePreview;