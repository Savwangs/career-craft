import React from 'react';
import { PlusIcon, XMarkIcon } from '@heroicons/react/24/outline';

export default function ResumeInput({ resumeData, setResumeData }) {

  if (!resumeData) {
    return <div>Loading...</div>;
  }

  const handleContactChange = (field, value) => {
    setResumeData({
      ...resumeData,
      contact_info: {
        ...resumeData.contact_info,
        [field]: value
      }
    });
  };

  const addExperience = () => {
    setResumeData({
      ...resumeData,
      experience: [
        ...resumeData.experience,
        {
          company: '',
          position: '',
          start_date: '',
          end_date: '',
          description: '',
          highlights: ['']
        }
      ]
    });
  };

  const addEducation = () => {
    setResumeData({
      ...resumeData,
      education: [
        ...resumeData.education,
        {
          institution: '',
          degree: '',
          field_of_study: '',
          start_date: '',
          end_date: '',
          gpa: ''
        }
      ]
    });
  };

  const addSkill = () => {
    setResumeData({
      ...resumeData,
      skills: [
        ...resumeData.skills,
        {
          name: '',
          category: ''
        }
      ]
    });
  };

  const addProject = () => {
    setResumeData({
      ...resumeData,
      projects: [
        ...resumeData.projects,
        {
          title: '',
          description: '',
          technologies: [],
          url: ''
        }
      ]
    });
  };

  const addAchievement = () => {
    setResumeData({
      ...resumeData,
      achievements: [
        ...resumeData.achievements,
        {
          title: '',
          description: '',
          date: ''
        }
      ]
    });
  };

  return (
    <div className="space-y-8">
      {/* Contact Information */}
      <section>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Contact Information</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <input
            type="text"
            placeholder="Full Name"
            value={resumeData.contact_info.name}
            onChange={(e) => handleContactChange('name', e.target.value)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
          <input
            type="email"
            placeholder="Email"
            value={resumeData.contact_info.email}
            onChange={(e) => handleContactChange('email', e.target.value)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
          <input
            type="tel"
            placeholder="Phone"
            value={resumeData.contact_info.phone}
            onChange={(e) => handleContactChange('phone', e.target.value)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
          <input
            type="text"
            placeholder="Location"
            value={resumeData.contact_info.location}
            onChange={(e) => handleContactChange('location', e.target.value)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
      </section>

      {/* Summary */}
      <section>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Professional Summary</h3>
        <textarea
          value={resumeData.summary}
          onChange={(e) => setResumeData({ ...resumeData, summary: e.target.value })}
          className="w-full h-32 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          placeholder="Write a brief professional summary..."
        />
      </section>

      {/* Experience */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Experience</h3>
          <button
            type="button"
            onClick={addExperience}
            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-600 bg-indigo-100 hover:bg-indigo-200"
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            Add Experience
          </button>
        </div>
        {resumeData.experience.map((exp, index) => (
          <div key={index} className="mb-6 p-4 border rounded-md">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <input
                type="text"
                placeholder="Company"
                value={exp.company}
                onChange={(e) => {
                  const newExp = [...resumeData.experience];
                  newExp[index].company = e.target.value;
                  setResumeData({ ...resumeData, experience: newExp });
                }}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <input
                type="text"
                placeholder="Position"
                value={exp.position}
                onChange={(e) => {
                  const newExp = [...resumeData.experience];
                  newExp[index].position = e.target.value;
                  setResumeData({ ...resumeData, experience: newExp });
                }}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <input
                type="month"
                placeholder="Start Date"
                value={exp.start_date}
                onChange={(e) => {
                  const newExp = [...resumeData.experience];
                  newExp[index].start_date = e.target.value;
                  setResumeData({ ...resumeData, experience: newExp });
                }}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <input
                type="month"
                placeholder="End Date"
                value={exp.end_date}
                onChange={(e) => {
                  const newExp = [...resumeData.experience];
                  newExp[index].end_date = e.target.value;
                  setResumeData({ ...resumeData, experience: newExp });
                }}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
            <textarea
              placeholder="Description"
              value={exp.description}
              onChange={(e) => {
                const newExp = [...resumeData.experience];
                newExp[index].description = e.target.value;
                setResumeData({ ...resumeData, experience: newExp });
              }}
              className="mt-4 w-full h-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
        ))}
      </section>

      {/* Education */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Education</h3>
          <button
            type="button"
            onClick={addEducation}
            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-600 bg-indigo-100 hover:bg-indigo-200"
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            Add Education
          </button>
        </div>
        {resumeData.education.map((edu, index) => (
          <div key={index} className="mb-6 p-4 border rounded-md">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <input
                type="text"
                placeholder="Institution"
                value={edu.institution}
                onChange={(e) => {
                  const newEdu = [...resumeData.education];
                  newEdu[index].institution = e.target.value;
                  setResumeData({ ...resumeData, education: newEdu });
                }}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <input
                type="text"
                placeholder="Degree"
                value={edu.degree}
                onChange={(e) => {
                  const newEdu = [...resumeData.education];
                  newEdu[index].degree = e.target.value;
                  setResumeData({ ...resumeData, education: newEdu });
                }}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <input
                type="text"
                placeholder="Field of Study"
                value={edu.field_of_study}
                onChange={(e) => {
                  const newEdu = [...resumeData.education];
                  newEdu[index].field_of_study = e.target.value;
                  setResumeData({ ...resumeData, education: newEdu });
                }}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <input
                type="text"
                placeholder="GPA"
                value={edu.gpa}
                onChange={(e) => {
                  const newEdu = [...resumeData.education];
                  newEdu[index].gpa = e.target.value;
                  setResumeData({ ...resumeData, education: newEdu });
                }}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <input
                type="month"
                placeholder="Start Date"
                value={edu.start_date}
                onChange={(e) => {
                  const newEdu = [...resumeData.education];
                  newEdu[index].start_date = e.target.value;
                  setResumeData({ ...resumeData, education: newEdu });
                }}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <input
                type="month"
                placeholder="End Date"
                value={edu.end_date}
                onChange={(e) => {
                  const newEdu = [...resumeData.education];
                  newEdu[index].end_date = e.target.value;
                  setResumeData({ ...resumeData, education: newEdu });
                }}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
          </div>
        ))}
      </section>

      {/* Skills */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Skills</h3>
          <button
            type="button"
            onClick={addSkill}
            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-600 bg-indigo-100 hover:bg-indigo-200"
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            Add Skill
          </button>
        </div>
        {resumeData.skills.map((skill, index) => (
          <div key={index} className="mb-4 flex gap-4">
            <input
              type="text"
              placeholder="Skill"
              value={skill.name}
              onChange={(e) => {
                const newSkills = [...resumeData.skills];
                newSkills[index].name = e.target.value;
                setResumeData({ ...resumeData, skills: newSkills });
              }}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
            <input
              type="text"
              placeholder="Category"
              value={skill.category}
              onChange={(e) => {
                const newSkills = [...resumeData.skills];
                newSkills[index].category = e.target.value;
                setResumeData({ ...resumeData, skills: newSkills });
              }}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
        ))}
      </section>

      {/* Projects */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Projects</h3>
          <button
            type="button"
            onClick={addProject}
            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-600 bg-indigo-100 hover:bg-indigo-200"
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            Add Project
          </button>
        </div>
        {resumeData.projects.map((project, index) => (
          <div key={index} className="mb-4 p-4 border rounded-md">
            <input
              type="text"
              placeholder="Title"
              value={project.title}
              onChange={(e) => {
                const newProjects = [...resumeData.projects];
                newProjects[index].title = e.target.value;
                setResumeData({ ...resumeData, projects: newProjects });
              }}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 mb-2"
            />
            <textarea
              placeholder="Description"
              value={project.description}
              onChange={(e) => {
                const newProjects = [...resumeData.projects];
                newProjects[index].description = e.target.value;
                setResumeData({ ...resumeData, projects: newProjects });
              }}
              className="w-full h-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 mb-2"
            />
            <input
              type="text"
              placeholder="Technologies"
              value={project.technologies.join(', ')}
              onChange={(e) => {
                const newProjects = [...resumeData.projects];
                newProjects[index].technologies = e.target.value.split(',').map((tech) => tech.trim());
                setResumeData({ ...resumeData, projects: newProjects });
              }}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
            <input
              type="text"
              placeholder="URL"
              value={project.url}
              onChange={(e) => {
                const newProjects = [...resumeData.projects];
                newProjects[index].url = e.target.value;
                setResumeData({ ...resumeData, projects: newProjects });
              }}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
        ))}
      </section>

      {/* Achievements */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Achievements</h3>
          <button
            type="button"
            onClick={addAchievement}
            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-600 bg-indigo-100 hover:bg-indigo-200"
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            Add Achievement
          </button>
        </div>
        {resumeData.achievements.map((achievement, index) => (
          <div key={index} className="mb-4 p-4 border rounded-md">
            <input
              type="text"
              placeholder="Title"
              value={achievement.title}
              onChange={(e) => {
                const newAchievements = [...resumeData.achievements];
                newAchievements[index].title = e.target.value;
                setResumeData({ ...resumeData, achievements: newAchievements });
              }}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 mb-2"
            />
            <textarea
              placeholder="Description"
              value={achievement.description}
              onChange={(e) => {
                const newAchievements = [...resumeData.achievements];
                newAchievements[index].description = e.target.value;
                setResumeData({ ...resumeData, achievements: newAchievements });
              }}
              className="w-full h-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 mb-2"
            />
            <input
              type="date"
              placeholder="Date"
              value={achievement.date}
              onChange={(e) => {
                const newAchievements = [...resumeData.achievements];
                newAchievements[index].date = e.target.value;
                setResumeData({ ...resumeData, achievements: newAchievements });
              }}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
        ))}
      </section>
    </div>
  );
}
