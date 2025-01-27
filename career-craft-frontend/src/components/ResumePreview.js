import React from 'react';
import { AlertCircle, Download, Edit2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function ResumePreview({ resumeData, feedback, recommendations, onDownload, onEdit, isUploadedResume = false }) {
  if (!resumeData) return null;

  const shouldRender = resumeData !== null;

  if (!shouldRender) return null;

  return (
    <div className="space-y-6">
      {(
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Resume Preview</CardTitle>
            <div className="space-x-2">
              <button
                onClick={onEdit}
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <Edit2 className="h-4 w-4 mr-2" />
                Edit
              </button>
              <button
                onClick={onDownload}
                className="inline-flex items-center px-3 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </button>
            </div>
          </CardHeader>
          <CardContent>
            {/* Contact Information */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold">{resumeData.contact_info?.name || 'Name Not Provided'}</h2>
              <div className="text-gray-600">
                <p>
                  {resumeData.contact_info?.email || 'Email Not Provided'} | 
                  {resumeData.contact_info?.phone || 'Phone Not Provided'}
                </p>
                <p>{resumeData.contact_info?.location || 'Location Not Provided'}</p>
              </div>
            </div>

            {/* Summary */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Professional Summary</h3>
              <p className="text-gray-700">{resumeData.summary || 'No summary provided'}</p>
            </div>

            {/* Experience */}
            {resumeData.experience?.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">Experience</h3>
                {resumeData.experience.map((exp, index) => (
                  <div key={index} className="mb-4">
                    <div className="flex justify-between">
                      <h4 className="font-medium">{exp.position || 'Position Not Specified'}</h4>
                      <span className="text-gray-600">
                        {exp.start_date ? new Date(exp.start_date).toLocaleDateString() : 'Start Date Unknown'} - 
                        {exp.end_date ? new Date(exp.end_date).toLocaleDateString() : 'Present'}
                      </span>
                    </div>
                    <p className="text-gray-700">{exp.company || 'Company Not Specified'}</p>
                    <p className="mt-2">{exp.description || 'No description provided'}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Education */}
            {resumeData.education?.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">Education</h3>
                {resumeData.education.map((edu, index) => (
                  <div key={index} className="mb-4">
                    <div className="flex justify-between">
                      <h4 className="font-medium">
                        {edu.degree ? `${edu.degree} in ${edu.field_of_study}` : 'Degree Not Specified'}
                      </h4>
                      <span className="text-gray-600">
                        {edu.start_date ? new Date(edu.start_date).toLocaleDateString() : 'Start Date Unknown'} - 
                        {edu.end_date ? new Date(edu.end_date).toLocaleDateString() : 'Present'}
                      </span>
                    </div>
                    <p className="text-gray-700">{edu.institution || 'Institution Not Specified'}</p>
                    {edu.gpa && <p className="text-gray-600">GPA: {edu.gpa}</p>}
                  </div>
                ))}
              </div>
            )}

              {/* Skills */}
              {resumeData.skills?.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {resumeData.skills.map((skill, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-700"
                      >
                        {skill.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

            {/* Projects */}
            {resumeData.projects?.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">Projects</h3>
                {resumeData.projects.map((project, index) => (
                  <div key={index} className="mb-4">
                    <h4 className="font-medium">{project.title || 'Project Not Named'}</h4>
                    <p className="text-gray-700">{project.description || 'No description provided'}</p>
                    {project.technologies?.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {project.technologies.map((tech, techIndex) => (
                          <span
                            key={techIndex}
                            className="px-2 py-1 bg-gray-100 rounded-full text-xs text-gray-700"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* AI Feedback */}
      {feedback && (
        <Card>
          <CardHeader>
            <CardTitle>Resume Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Overall Score */}
              <div className="flex items-center justify-between">
                <span className="text-lg font-medium">Overall Match Score:</span>
                <span className="text-2xl font-bold text-indigo-600">
                  {Math.round(feedback.overall_score * 100)}%
                </span>
              </div>

              {/* Improvement Areas */}
              {Object.entries(feedback.improvement_areas).map(([area, suggestions]) => (
                <Alert key={area} variant="info">
                  <AlertCircle className="h-4 w-4" />
                  <div className="ml-2">
                    <h4 className="font-medium">{area}</h4>
                    <AlertDescription>
                      <ul className="list-disc list-inside">
                        {suggestions.map((suggestion, index) => (
                          <li key={index}>{suggestion}</li>
                        ))}
                      </ul>
                    </AlertDescription>
                  </div>
                </Alert>
              ))}

              {/* Missing Skills */}
              {feedback.missing_skills.length > 0 && (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <div className="ml-2">
                    <h4 className="font-medium">Missing Skills</h4>
                    <AlertDescription>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {feedback.missing_skills.map((skill, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-sm"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </AlertDescription>
                  </div>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Job Recommendations */}
      {recommendations?.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recommended Job Matches</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recommendations.map((job, index) => (
                <div
                  key={index}
                  className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <h4 className="text-lg font-medium">{job.title}</h4>
                    <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm">
                      {Math.round(job.match_score * 100)}% Match
                    </span>
                  </div>
                  <p className="text-gray-600 mt-1">{job.category}</p>
                  <div className="mt-2">
                    <h5 className="font-medium">Key Responsibilities:</h5>
                    <ul className="list-disc list-inside text-gray-700">
                      {job.key_responsibilities.map((resp, respIndex) => (
                        <li key={respIndex}>{resp}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="mt-2">
                    <h5 className="font-medium">Required Skills:</h5>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {job.required_skills.map((skill, skillIndex) => (
                        <span
                          key={skillIndex}
                          className="px-2 py-1 bg-gray-100 rounded-full text-sm"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}