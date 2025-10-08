// src/forms/WorkForm.tsx
import React from 'react';
import { v4 as uuidv4 } from 'uuid';
import { WorkExperience } from '../types';

interface WorkFormProps {
  data: WorkExperience[];
  setData: (data: WorkExperience[]) => void;
}

const WorkForm: React.FC<WorkFormProps> = ({ data, setData }) => {
  const handleChange = (id: string, e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const newData = data.map(item => item.id === id ? { ...item, [e.target.name]: e.target.value } : item);
    setData(newData);
  };

  const addExperience = () => {
    setData([...data, { id: uuidv4(), job_title: '', company_name: '', location: '', start_date: '', end_date: '', description_points: '' }]);
  };

  const removeExperience = (id: string) => {
    setData(data.filter(item => item.id !== id));
  };

  return (
    <div className="form-section">
      <h2>Work Experience</h2>
      {data.map(item => (
        <div className="form-group" key={item.id}>
          <input type="text" name="job_title" placeholder="Job Title (e.g., Software Engineer)" value={item.job_title} onChange={e => handleChange(item.id, e)} />
          <input type="text" name="company_name" placeholder="Company Name" value={item.company_name} onChange={e => handleChange(item.id, e)} />
          <input type="text" name="location" placeholder="Location (e.g., City, Country)" value={item.location} onChange={e => handleChange(item.id, e)} />
          <input type="text" name="start_date" placeholder="Start Date (e.g., Jan 2022)" value={item.start_date} onChange={e => handleChange(item.id, e)} />
          <input type="text" name="end_date" placeholder="End Date (e.g., Present)" value={item.end_date} onChange={e => handleChange(item.id, e)} />
          <textarea name="description_points" placeholder="Job Description (one bullet point per line)" rows={5} value={item.description_points} onChange={e => handleChange(item.id, e)}></textarea>
          {data.length > 1 && <button className="btn-remove" onClick={() => removeExperience(item.id)}>Remove</button>}
        </div>
      ))}
      <button className="btn btn-outline" onClick={addExperience}>+ Add Experience</button>
    </div>
  );
};

export default WorkForm;