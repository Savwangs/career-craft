import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { resumeService } from '../services/resumeService';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export default function ResumeDetail() {
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { id } = useParams();

  useEffect(() => {
    const fetchResumeDetails = async () => {
      try {
        const resumeData = await resumeService.getResume(id);
        const feedback = await resumeService.analyzeResume(id, resumeData.target_job_description);
        const jobRecommendations = await resumeService.getJobRecommendations(id);

        setResume({
          ...resumeData,
          feedback,
          jobRecommendations
        });
        setLoading(false);
      } catch (err) {
        setError('Failed to load resume details');
        setLoading(false);
      }
    };

    fetchResumeDetails();
  }, [id]);

  if (loading) return <div>Loading resume...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>{resume.title}</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Display resume details here */}
          <h2>Resume Details</h2>
          {/* Add more detailed rendering of resume content */}
          
          <h3>Feedback</h3>
          <pre>{JSON.stringify(resume.feedback, null, 2)}</pre>
          
          <h3>Job Recommendations</h3>
          <pre>{JSON.stringify(resume.jobRecommendations, null, 2)}</pre>
        </CardContent>
      </Card>
    </div>
  );
}