import React from 'react';
import { DownloadLinks } from '../types';

interface PreviewPanelProps {
  isLoading: boolean;
  downloadLinks: DownloadLinks | null;
  errorMessage: string;
  previewPdfUrl: string | null;
}

const PreviewPanel: React.FC<PreviewPanelProps> = ({ isLoading, downloadLinks, errorMessage, previewPdfUrl }) => {
  
  const loadingMessage = isLoading ? <h4>Compiling PDF...</h4> : null;

  // Final download links have the highest priority to be shown
  if (downloadLinks) {
    return (
      <div className="download-links-container">
        <h4>Your resume is ready!</h4>
        <a href={downloadLinks.pdfUrl} className="btn btn-outline download-link" target="_blank" rel="noopener noreferrer">Download PDF</a>
        <a href={downloadLinks.latexUrl} className="btn btn-outline download-link" download>Download LaTeX</a>
        <a href={downloadLinks.jsonUrl} className="btn btn-outline download-link" download>Download JSON</a>
      </div>
    );
  }

  // Display an error message if one exists
  if (errorMessage) {
    return <p style={{ color: '#ff5c5c', fontWeight: 500 }}>Error: {errorMessage}</p>;
  }
  
  // Show the embedded live preview using the <object> tag
  if (previewPdfUrl) {
    return (
      <>
        {loadingMessage}
        <object 
          data={previewPdfUrl} 
          type="application/pdf"
          style={{ width: '100%', height: isLoading ? '95%' : '100%', border: 'none', transition: 'height 0.3s ease-in-out' }} 
        >
          {/* Fallback content if the browser cannot display the PDF */}
          <p>It appears you don't have a PDF plugin for this browser. You can <a href={previewPdfUrl}>click here to download the PDF file.</a></p>
        </object>
      </>
    );
  }

  // Default initial message or loading message
  return (
    <div>
        {loadingMessage}
        <p>Your resume preview will appear here as you type.</p>
    </div>
  );
};

export default PreviewPanel;