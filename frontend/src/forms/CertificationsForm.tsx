import React from 'react';
import { v4 as uuidv4 } from 'uuid';
import { CertificationItem } from '../types';

interface CertificationsFormProps {
  data: CertificationItem[];
  setData: (data: CertificationItem[]) => void;
}

const CertificationsForm: React.FC<CertificationsFormProps> = ({ data, setData }) => {
  const handleChange = (id: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const newData = data.map(item =>
      item.id === id ? { ...item, [e.target.name]: e.target.value } : item
    );
    setData(newData);
  };

  const addCertification = () => {
    setData([...data, { id: uuidv4(), name: '', issuer: '', date: '' }]);
  };

  const removeCertification = (id: string) => {
    setData(data.filter(item => item.id !== id));
  };

  return (
    <div className="form-section">
      <h2>Certifications</h2>
      {data.map((item) => (
        <div className="form-group" key={item.id}>
          <input type="text" name="name" placeholder="Certification Name (e.g., AWS Certified Developer)" value={item.name} onChange={e => handleChange(item.id, e)} />
          <input type="text" name="issuer" placeholder="Issuing Organization (e.g., Amazon Web Services)" value={item.issuer} onChange={e => handleChange(item.id, e)} />
          <input type="text" name="date" placeholder="Date (e.g., Sep 2025)" value={item.date} onChange={e => handleChange(item.id, e)} />
          {data.length > 1 && <button className="btn-remove" onClick={() => removeCertification(item.id)}>Remove</button>}
        </div>
      ))}
      <button className="btn btn-outline" onClick={addCertification}>+ Add Certification</button>
    </div>
  );
};

export default CertificationsForm;