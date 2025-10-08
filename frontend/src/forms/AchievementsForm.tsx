import React from 'react';
import { v4 as uuidv4 } from 'uuid';
import { AchievementItem } from '../types';

interface AchievementsFormProps {
  data: AchievementItem[];
  setData: (data: AchievementItem[]) => void;
}

const AchievementsForm: React.FC<AchievementsFormProps> = ({ data, setData }) => {
  const handleChange = (id: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const newData = data.map(item => 
      item.id === id ? { ...item, [e.target.name]: e.target.value } : item
    );
    setData(newData);
  };

  const addAchievement = () => {
    setData([...data, { id: uuidv4(), description: '' }]);
  };

  const removeAchievement = (id: string) => {
    setData(data.filter(item => item.id !== id));
  };

  return (
    <div className="form-section">
      <h2>Achievements</h2>
      {data.map((item) => (
        <div className="form-group" key={item.id}>
          <input 
            type="text" 
            name="description" 
            placeholder="e.g., Winner of National Hackathon 2025" 
            value={item.description} 
            onChange={(e) => handleChange(item.id, e)} 
          />
          {data.length > 1 && <button className="btn-remove" onClick={() => removeAchievement(item.id)}>Remove</button>}
        </div>
      ))}
      <button className="btn btn-outline" onClick={addAchievement}>+ Add Achievement</button>
    </div>
  );
};

export default AchievementsForm;