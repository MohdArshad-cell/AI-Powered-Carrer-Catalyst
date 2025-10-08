import React from 'react';

// Step 1: Import your preview images
import professionalPreview from '../assets/professional_preview.png'; 
import elegantPreview from '../assets/elegant_preview.png';
import modernlinePreview from '../assets/modern_line_preview.png';
import onecolumnPreview from '../assets/one_column_preview.png';  
// As you create more previews, you'll import them here too.

const templates = [
  
  'Professional',
  'Elegant',
  'Modern Line',
  'One Column',
  
];

// Step 2: Create a map to link template names to the imported images
const imageMap: { [key: string]: string } = {
  'Professional': professionalPreview,
  'Elegant': elegantPreview,
  'Modern Line': modernlinePreview,
  'One Column': onecolumnPreview,
};

interface TemplateSelectionProps {
  selectedTemplate: string;
  setSelectedTemplate: (template: string) => void;
}

const TemplateSelection: React.FC<TemplateSelectionProps> = ({ selectedTemplate, setSelectedTemplate }) => {
  return (
    <div className="form-section template-gallery">
      <h2>Choose a Template</h2>
      <div className="template-grid">
        {templates.map(template => (
          <div
            key={template}
            className={`template-card ${selectedTemplate === template ? 'active' : ''}`}
            onClick={() => setSelectedTemplate(template)}
          >
            {/* Step 3: Use an <img> tag to display the image from the map */}
            <img 
              src={imageMap[template]} 
              alt={`${template} resume template preview`} 
              className="template-preview-img"
            />
            <p>{template}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TemplateSelection;