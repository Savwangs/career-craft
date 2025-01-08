import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { apiService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const ResumePreview = ({ resumeContent, jobDescription }) => {
  const [feedback, setFeedback] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { currentUser } = useAuth();

  useEffect(() => {
    const fetchFeedbackAndRecommendations = async () => {
      if (!resumeContent || !jobDescription) {
        setError('Both resume and job description are required');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const [feedbackData, recommendationsData] = await Promise.all([
          apiService.getResumeFeedback(currentUser.token, resumeContent, jobDescription),
          apiService.getJobRecommendations(currentUser.token, resumeContent, jobDescription)
        ]);
        setFeedback(feedbackData);
        setRecommendations(recommendationsData);
      } catch (err) {
        setError('Failed to load feedback and recommendations');
      } finally {
        setLoading(false);
      }
    };

    fetchFeedbackAndRecommendations();
  }, [resumeContent, jobDescription, currentUser]);

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
          <div className="prose max-w-none">
            {resumeContent}
          </div>
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
                    {job.requiredSkills.map((skill, idx) => (
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