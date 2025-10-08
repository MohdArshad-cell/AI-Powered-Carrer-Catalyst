// src/forms/ProjectsForm.tsx
import React from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Project } from '../types';

interface ProjectsFormProps {
  data: Project[];
  setData: (data: Project[]) => void;
}

const ProjectsForm: React.FC<ProjectsFormProps> = ({ data, setData }) => {
  const handleChange = (id: string, e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const newData = data.map(item => item.id === id ? { ...item, [e.target.name]: e.target.value } : item);
    setData(newData);
  };

  const addProject = () => {
    setData([...data, { id: uuidv4(), project_name: '', start_date: '', end_date: '', tech_stack: '', description_points: '' }]);
  };

  const removeProject = (id: string) => {
    setData(data.filter(item => item.id !== id));
  };

  return (
    <div className="form-section">
      <h2>Projects</h2>
      {data.map(item => (
        <div className="form-group" key={item.id}>
          <input type="text" name="project_name" placeholder="Project Name" value={item.project_name} onChange={e => handleChange(item.id, e)} />
          <input type="text" name="start_date" placeholder="Start Date (e.g., Jan 2025)" value={item.start_date} onChange={e => handleChange(item.id, e)} />
          <input type="text" name="end_date" placeholder="End Date (e.g., Mar 2025)" value={item.end_date} onChange={e => handleChange(item.id, e)} />
          <input type="text" name="tech_stack" placeholder="Tech Stack (e.g., Java, Spring Boot, React)" value={item.tech_stack} onChange={e => handleChange(item.id, e)} />
          <textarea name="description_points" placeholder="Project Description (one bullet point per line)" rows={5} value={item.description_points} onChange={e => handleChange(item.id, e)}></textarea>
          {data.length > 1 && <button className="btn-remove" onClick={() => removeProject(item.id)}>Remove</button>}
        </div>
      ))}
      <button className="btn btn-outline" onClick={addProject}>+ Add Project</button>
    </div>
  );
};

export default ProjectsForm;