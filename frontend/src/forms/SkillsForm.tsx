import React from 'react';
import { v4 as uuidv4 } from 'uuid';
import { SkillItem } from '../types';

interface SkillsFormProps {
  data: SkillItem[];
  setData: (data: SkillItem[]) => void;
}

const SkillsForm: React.FC<SkillsFormProps> = ({ data, setData }) => {
  const handleChange = (id: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const newData = data.map(item => {
      if (item.id === id) {
        return { ...item, [e.target.name]: e.target.value };
      }
      return item;
    });
    setData(newData);
  };

  const addSkill = () => {
    setData([...data, { id: uuidv4(), name: '', value: '' }]);
  };

  const removeSkill = (id: string) => {
    setData(data.filter(item => item.id !== id));
  };

  return (
    <div className="form-section">
      <h2>Technical Skills</h2>
      {data.map((skillItem) => (
        <div className="form-group" key={skillItem.id}>
          <input 
            type="text" 
            name="name" 
            placeholder="Skill Category (e.g., Languages)" 
            value={skillItem.name} 
            onChange={(e) => handleChange(skillItem.id, e)} 
          />
          <input 
            type="text" 
            name="value" 
            placeholder="Skills (e.g., Java, Python, SQL)" 
            value={skillItem.value} 
            onChange={(e) => handleChange(skillItem.id, e)} 
          />
          {data.length > 1 && <button className="btn-remove" onClick={() => removeSkill(skillItem.id)}>Remove</button>}
        </div>
      ))}
      <button className="btn btn-outline" onClick={addSkill}>+ Add Skill</button>
    </div>
  );
};

export default SkillsForm;