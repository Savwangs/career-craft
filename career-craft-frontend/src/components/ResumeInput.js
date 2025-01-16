import React, { useState } from 'react';

const ResumeInput = ({ onSubmit }) => {
  // State for form/upload method selection
  const [inputMethod, setInputMethod] = useState('form');
  
  // State for job description
  const [jobDescription, setJobDescription] = useState('');
  
  // State for form data
  const [formData, setFormData] = useState({
    personalInfo: {
      fullName: '',
      email: '',
      phone: '',
      location: '',
    },
    summary: '',
    experience: [{
      title: '',
      company: '',
      startDate: '',
      endDate: '',
      description: '',
      isCurrentPosition: false,
    }],
    education: [{
      degree: '',
      institution: '',
      graduationDate: '',
      gpa: '',
      relevantCourses: [{
        courseName: '',
        skillsLearned: ''
      }]
    }],
    skills: '',
    achievements: [{
      title: '',
      description: '',
      date: '',
    }]
  });
  
  // State for file upload
  const [resumeFile, setResumeFile] = useState(null);
  
  // State for error messages
  const [error, setError] = useState('');

  const handleFormChange = (section, field, value, index = null, courseIndex = null) => {
    setFormData(prev => {
      if (courseIndex !== null) {
        const newEducation = [...prev.education];
        const newCourses = [...newEducation[index].relevantCourses];
        newCourses[courseIndex] = { ...newCourses[courseIndex], [field]: value };
        newEducation[index] = { ...newEducation[index], relevantCourses: newCourses };
        return { ...prev, education: newEducation };
      }
      
      if (index !== null) {
        const newSection = [...prev[section]];
        newSection[index] = { ...newSection[index], [field]: value };
        return { ...prev, [section]: newSection };
      }
      
      if (section === 'personalInfo') {
        return {
          ...prev,
          personalInfo: { ...prev.personalInfo, [field]: value }
        };
      }
      
      return { ...prev, [section]: value };
    });
  };

  const addListItem = (section, educationIndex = null) => {
    if (educationIndex !== null) {
      setFormData(prev => {
        const newEducation = [...prev.education];
        newEducation[educationIndex] = {
          ...newEducation[educationIndex],
          relevantCourses: [...newEducation[educationIndex].relevantCourses, { courseName: '', skillsLearned: '' }]
        };
        return { ...prev, education: newEducation };
      });
      return;
    }

    const newItem = {
      experience: { title: '', company: '', startDate: '', endDate: '', description: '', isCurrentPosition: false },
      education: { degree: '', institution: '', graduationDate: '', gpa: '', relevantCourses: [{ courseName: '', skillsLearned: '' }] },
      achievements: { title: '', description: '', date: '' }
    }[section];

    setFormData(prev => ({
      ...prev,
      [section]: [...prev[section], newItem]
    }));
  };

  const removeListItem = (section, index, educationIndex = null, courseIndex = null) => {
    if (courseIndex !== null) {
      setFormData(prev => {
        const newEducation = [...prev.education];
        const newCourses = newEducation[educationIndex].relevantCourses.filter((_, i) => i !== courseIndex);
        newEducation[educationIndex] = { ...newEducation[educationIndex], relevantCourses: newCourses };
        return { ...prev, education: newEducation };
      });
      return;
    }

    setFormData(prev => ({
      ...prev,
      [section]: prev[section].filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!jobDescription) {
        setError('Please provide a job description');
        return;
    }

    if (inputMethod === 'form') {
        if (!formData || !formData.personalInfo || !formData.personalInfo.fullName) {
            setError('Please provide your full name.');
            return;
        }

        if (!formData.experience || formData.experience.length === 0) {
            setError('Please add at least one experience entry.');
            return;
        }
    }

    if (inputMethod === 'upload' && !resumeFile) {
        setError('Please upload your resume.');
        return;
    }

    try {
        console.log('Submitting data:', {
            inputMethod,
            data: inputMethod === 'form' ? formData : resumeFile,
            jobDescription
        });

        await onSubmit({
            inputMethod,
            data: inputMethod === 'form' ? formData : resumeFile,  // 🔄 Correct key is `data`
            jobDescription
        });
    } catch (err) {
        console.error('Resume submission error:', err);
        setError(err.message || 'Failed to process resume');
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold">Create Your Resume</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Tabs */}
        <div className="border-b border-gray-200">
          <div className="flex space-x-4">
            <button
              type="button"
              className={`py-2 px-4 ${inputMethod === 'form' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500'}`}
              onClick={() => setInputMethod('form')}
            >
              Fill Form
            </button>
            <button
              type="button"
              className={`py-2 px-4 ${inputMethod === 'upload' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500'}`}
              onClick={() => setInputMethod('upload')}
            >
              Upload Resume
            </button>
          </div>
        </div>

        {inputMethod === 'form' ? (
          <div className="space-y-6">
            {/* Personal Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Personal Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <input
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Full Name"
                  value={formData.personalInfo.fullName}
                  onChange={(e) => handleFormChange('personalInfo', 'fullName', e.target.value)}
                />
                <input
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Email"
                  type="email"
                  value={formData.personalInfo.email}
                  onChange={(e) => handleFormChange('personalInfo', 'email', e.target.value)}
                />
                <input
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Phone"
                  value={formData.personalInfo.phone}
                  onChange={(e) => handleFormChange('personalInfo', 'phone', e.target.value)}
                />
                <input
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Location"
                  value={formData.personalInfo.location}
                  onChange={(e) => handleFormChange('personalInfo', 'location', e.target.value)}
                />
              </div>
            </div>

            {/* Professional Summary */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Professional Summary</h3>
                <span className="text-sm text-gray-500">{formData.summary.length}/100 characters</span>
              </div>
              <textarea
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="Write a brief professional summary..."
                rows={4}
                value={formData.summary}
                onChange={(e) => handleFormChange('summary', null, e.target.value)}
                maxLength={100}
              />
            </div>

            {/* Experience Section */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Experience</h3>
                <button
                  type="button"
                  className="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                  onClick={() => addListItem('experience')}
                >
                  Add Experience
                </button>
              </div>
              {formData.experience.map((exp, index) => (
                <div key={index} className="space-y-4 p-4 border rounded-lg">
                  <div className="grid grid-cols-2 gap-4">
                    <input
                      className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="Job Title"
                      value={exp.title}
                      onChange={(e) => handleFormChange('experience', 'title', e.target.value, index)}
                    />
                    <input
                      className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="Company"
                      value={exp.company}
                      onChange={(e) => handleFormChange('experience', 'company', e.target.value, index)}
                    />
                    <div className="flex items-center space-x-2">
                      <input
                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                        type="date"
                        value={exp.startDate}
                        onChange={(e) => handleFormChange('experience', 'startDate', e.target.value, index)}
                      />
                      <span>to</span>
                      <input
                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                        type="date"
                        value={exp.endDate}
                        onChange={(e) => handleFormChange('experience', 'endDate', e.target.value, index)}
                        disabled={exp.isCurrentPosition}
                      />
                    </div>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        className="mr-2"
                        checked={exp.isCurrentPosition}
                        onChange={(e) => handleFormChange('experience', 'isCurrentPosition', e.target.checked, index)}
                      />
                      <label>Current Position</label>
                    </div>
                  </div>
                  <textarea
                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder="Description of responsibilities and achievements..."
                    rows={3}
                    value={exp.description}
                    onChange={(e) => handleFormChange('experience', 'description', e.target.value, index)}
                  />
                  {index > 0 && (
                    <button
                      type="button"
                      className="px-4 py-2 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                      onClick={() => removeListItem('experience', index)}
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
            </div>

            {/* Education */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Education</h3>
                <button
                  type="button"
                  className="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                  onClick={() => addListItem('education')}
                >
                  Add Education
                </button>
              </div>
              {formData.education.map((edu, index) => (
                <div key={index} className="space-y-4 p-4 border rounded-lg">
                  <div className="grid grid-cols-2 gap-4">
                    <input
                      className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="Degree"
                      value={edu.degree}
                      onChange={(e) => handleFormChange('education', 'degree', e.target.value, index)}
                    />
                    <input
                      className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="Institution"
                      value={edu.institution}
                      onChange={(e) => handleFormChange('education', 'institution', e.target.value, index)}
                    />
                    <input
                      className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="Graduation Date"
                      type="date"
                      value={edu.graduationDate}
                      onChange={(e) => handleFormChange('education', 'graduationDate', e.target.value, index)}
                    />
                    <input
                      className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="GPA (optional)"
                      value={edu.gpa}
                      onChange={(e) => handleFormChange('education', 'gpa', e.target.value, index)}
                    />
                  </div>
                  
                  {/* Relevant Coursework Section */}
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h4 className="text-md font-medium">Relevant Coursework</h4>
                      <button
                        type="button"
                        className="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                        onClick={() => addListItem('education', index)}
                      >
                        Add Course
                      </button>
                    </div>
                    {edu.relevantCourses.map((course, courseIndex) => (
                      <div key={courseIndex} className="space-y-2 p-4 border rounded-lg bg-gray-50">
                        <input
                          className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                          placeholder="Course Name"
                          value={course.courseName}
                          onChange={(e) => handleFormChange('education', 'courseName', e.target.value, index, courseIndex)}
                        />
                        <textarea
                          className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                          placeholder="Skills Learned in Course"
                          rows={2}
                          value={course.skillsLearned}
                          onChange={(e) => handleFormChange('education', 'skillsLearned', e.target.value, index, courseIndex)}
                        />
                        {courseIndex > 0 && (
                          <button
                            type="button"
                            className="px-4 py-2 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                            onClick={() => removeListItem('education', null, index, courseIndex)}
                          >
                            Remove Course
                          </button>
                        )}
                      </div>
                    ))}
                  </div>

                  {index > 0 && (
                    <button
                      type="button"
                      className="px-4 py-2 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                      onClick={() => removeListItem('education', index)}
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
            </div>

            {/* Skills */}
            <div className="space-y-2">
              <h3 className="text-lg font-medium">Skills</h3>
              <textarea
                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="List your key skills (comma separated)..."
                rows={3}
                value={formData.skills}
                onChange={(e) => handleFormChange('skills', null, e.target.value)}
              />
            </div>

            {/* New Achievements Section */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Additional Accomplishments/Awards (Optional)</h3>
                <button
                  type="button"
                  className="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                  onClick={() => addListItem('achievements')}
                >
                  Add Achievement
                </button>
              </div>
              {formData.achievements.map((achievement, index) => (
                <div key={index} className="space-y-4 p-4 border rounded-lg">
                  <div className="grid grid-cols-2 gap-4">
                    <input
                      className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="Achievement Title"
                      value={achievement.title}
                      onChange={(e) => handleFormChange('achievements', 'title', e.target.value, index)}
                    />
                    <input
                      className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                      type="date"
                      value={achievement.date}
                      onChange={(e) => handleFormChange('achievements', 'date', e.target.value, index)}
                    />
                  </div>
                  <textarea
                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder="Description of achievement..."
                    rows={2}
                    value={achievement.description}
                    onChange={(e) => handleFormChange('achievements', 'description', e.target.value, index)}
                  />
                  <button
                    type="button"
                    className="px-4 py-2 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                    onClick={() => removeListItem('achievements', index)}
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(e) => setResumeFile(e.target.files[0])}
              className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
            />
            <p className="text-sm text-gray-500">
              Supported formats: PDF, DOC, DOCX
            </p>
          </div>
        )}

        {/* Job Description */}
        <div className="space-y-2">
          <h3 className="text-lg font-medium">Job Description</h3>
          <textarea
            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="Paste the job description you're targeting..."
            rows={6}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Generate Resume
        </button>
      </form>
    </div>
  );
};

export default ResumeInput;