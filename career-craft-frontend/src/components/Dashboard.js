import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { resumeService } from '../services/resumeService';

export default function Dashboard() {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user, getToken } = useAuth();

  const loadResumes = async () => {
    try {
      const token = await getToken();
      if (!token) throw new Error('No authentication token available');
  
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/resumes`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
  
      if (!response.ok) {
        throw new Error('Failed to fetch resumes');
      }
  
      const data = await response.json();
      setResumes(data);
    } catch (err) {
      console.error('Error loading resumes:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      loadResumes();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <Card>
          <CardContent className="p-6">
            <div className="text-center">Loading...</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const handleDeleteResume = async (resumeId) => {
    try {
      await resumeService.deleteResume(resumeId);
      // Remove the deleted resume from the local state
      setResumes(resumes.filter(resume => resume.id !== resumeId));
    } catch (err) {
      console.error('Delete resume error:', err);
      setError('Failed to delete resume');
    }
  };

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Your Resumes</CardTitle>
        </CardHeader>
        <CardContent>
          {resumes.length === 0 ? (
            <div className="text-center">
              <p className="mb-4">You haven't created any resumes yet.</p>
              <Link
                to="/resume/new"
                className="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Create Your First Resume
              </Link>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {resumes.map(resume => (
                <div key={resume.id} className="relative">
                  <Link to={`/resume/${resume.id}`}>
                    <Card className="hover:shadow-lg transition-shadow">
                      <CardContent className="p-4">
                        <h3 className="font-semibold">{resume.title || 'Untitled Resume'}</h3>
                        <p className="text-sm text-gray-500">
                          Last updated: {new Date(resume.updated_at).toLocaleDateString()}
                        </p>
                      </CardContent>
                    </Card>
                  </Link>
                  <button 
                    onClick={(e) => {
                      e.preventDefault(); // Prevent navigation
                      handleDeleteResume(resume.id);
                    }}
                    className="absolute top-2 right-2 text-red-500 hover:text-red-700 z-10"
                  >
                    🗑️
                  </button>
                </div>
              ))}
              <Link
                to="/resume/new"
                className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-gray-400 transition-colors"
              >
                <span className="text-gray-600">+ Create New Resume</span>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}