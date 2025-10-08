// src/forms/ProfileForm.tsx
import React from 'react';
import { PersonalInfo } from '../types';

interface ProfileFormProps {
  data: PersonalInfo;
  setData: (data: PersonalInfo) => void;
}

const ProfileForm: React.FC<ProfileFormProps> = ({ data, setData }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setData({ ...data, [e.target.name]: e.target.value });
  };

  return (
    <div className="form-section">
      <h2>Your Personal Info</h2>
      <div className="form-group">
        <input type="text" name="full_name" placeholder="Full Name" value={data.full_name} onChange={handleChange} />
        <input type="text" name="address" placeholder="Address" value={data.address} onChange={handleChange} />
        <input type="email" name="email" placeholder="Email" value={data.email} onChange={handleChange} />
        <input type="tel" name="phone" placeholder="Phone Number" value={data.phone} onChange={handleChange} />
        <input type="text" name="github_handle" placeholder="GitHub Handle (e.g., johndoe)" value={data.github_handle} onChange={handleChange} />
        <input type="text" name="linkedin_handle" placeholder="LinkedIn Handle (e.g., johndoe)" value={data.linkedin_handle} onChange={handleChange} />
        <input type="text" name="portfolio_url" placeholder="Portfolio Website URL" value={data.portfolio_url} onChange={handleChange} />
    
      </div>
    </div>
  );
};

export default ProfileForm;