import React from 'react';
import { apiService } from '../services/api';
import { authService } from '../services/auth';

const ResumeList = ({ resumes, setResumes }) => {
  const handleDelete = async (id) => {
    try {
      const token = authService.getToken();
      await apiService.deleteResume(token, id);
      setResumes(resumes.filter(resume => resume.id !== id));
    } catch (error) {
      console.error('Failed to delete resume:', error);
    }
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {resumes.map((resume) => (
        <div key={resume.id} className="bg-white p-4 rounded-lg shadow">
          <div className="mb-4">
            <h3 className="text-lg font-semibold">Resume #{resume.id}</h3>
            <p className="text-gray-600">
              Created: {new Date(resume.created_at).toLocaleDateString()}
            </p>
          </div>
          <div className="flex justify-end space-x-2">
            <button
              onClick={() => handleDelete(resume.id)}
              className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
            >
              Delete
            </button>
          </div>
        </div>
      ))}
      {resumes.length === 0 && (
        <p className="text-gray-500">No resumes found. Create your first resume!</p>
      )}
    </div>
  );
};

export default ResumeList;