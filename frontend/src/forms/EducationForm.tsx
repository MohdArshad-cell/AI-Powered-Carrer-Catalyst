// src/forms/EducationForm.tsx
import React from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Education } from '../types';

interface EducationFormProps {
  data: Education[];
  setData: (data: Education[]) => void;
}

const EducationForm: React.FC<EducationFormProps> = ({ data, setData }) => {
  const handleChange = (id: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const newData = data.map(edu => {
      if (edu.id === id) {
        return { ...edu, [e.target.name]: e.target.value };
      }
      return edu;
    });
    setData(newData);
  };

  const addEducation = () => {
    setData([...data, { id: uuidv4(), degree: '', institution: '', start_year: '', end_year: '', gpa: '' }]);
  };

  const removeEducation = (id: string) => {
    setData(data.filter(edu => edu.id !== id));
  };

  return (
    <div className="form-section">
      <h2>Education</h2>
      {data.map((eduItem) => (
        <div className="form-group" key={eduItem.id}>
          <input type="text" name="degree" placeholder="Degree (e.g., Bachelor of Technology)" value={eduItem.degree} onChange={(e) => handleChange(eduItem.id, e)} />
          <input type="text" name="institution" placeholder="Institution Name" value={eduItem.institution} onChange={(e) => handleChange(eduItem.id, e)} />
          <input type="text" name="start_year" placeholder="Start Year" value={eduItem.start_year} onChange={(e) => handleChange(eduItem.id, e)} />
          <input type="text" name="end_year" placeholder="End Year" value={eduItem.end_year} onChange={(e) => handleChange(eduItem.id, e)} />
          <input type="text" name="gpa" placeholder="GPA / Grade" value={eduItem.gpa} onChange={(e) => handleChange(eduItem.id, e)} />
          {data.length > 1 && <button className="btn-remove" onClick={() => removeEducation(eduItem.id)}>Remove</button>}
        </div>
      ))}
      <button className="btn btn-outline" onClick={addEducation}>+ Add Education</button>
    </div>
  );
};

export default EducationForm;