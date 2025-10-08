import React, { useState } from 'react';
import axios from 'axios';
import { saveAs } from 'file-saver';
import jsPDF from 'jspdf'; // Import jsPDF for PDF generation
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ParticleBackground from '../components/ParticleBackground';
import './AiTailorPage.css'; // Reuse the same CSS for a consistent look

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080';

const CoverLetterGeneratorPage: React.FC = () => {
    // State variables adapted for the cover letter generator
    const [resume, setResume] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [generatedCoverLetter, setGeneratedCoverLetter] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [copyButtonText, setCopyButtonText] = useState('Copy');

    // API call handler adapted for generating a cover letter
    const handleGenerateCoverLetter = async () => {
        if (!resume || !jobDescription) {
            setError('Please provide both your resume and the job description.');
            return;
        }
        setIsLoading(true);
        setError('');
        setGeneratedCoverLetter('');
        setCopyButtonText('Copy');

        try {
            const payload = { resume, jobDescription };
            // IMPORTANT: Updated API endpoint for the cover letter
            const response = await axios.post(`${API_BASE_URL}/api/v1/generate-cover-letter`, payload);
            // IMPORTANT: Using the correct response key from your backend
            setGeneratedCoverLetter(response.data.generatedCoverLetter);
        } catch (err) {
            console.error("Error generating cover letter:", err);
            setError('Failed to generate cover letter. The service may be down.');
        } finally {
            setIsLoading(false);
        }
    };

    const handlePdfDownload = () => {
        const doc = new jsPDF();
        // The splitTextToSize method handles text wrapping automatically
        const lines = doc.splitTextToSize(generatedCoverLetter, 180); // 180 is max line width
        doc.text(lines, 10, 10);
        doc.save('cover_letter.pdf');
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(generatedCoverLetter).then(() => {
            setCopyButtonText('Copied!');
            setTimeout(() => setCopyButtonText('Copy'), 2000);
        }, (err) => {
            console.error('Could not copy text: ', err);
            setCopyButtonText('Failed!');
        });
    };

    return (
        <div className="page-container">
            <ParticleBackground />
            <div className="background-aurora"></div>
            <Navbar />

            <div className="tailor-container">
                <div className="tailor-header">
                    <h1>AI Cover Letter Generator</h1>
                    <p>Create a compelling cover letter tailored to any job in seconds.</p>
                </div>

                <div className="tailor-grid">
                    <div className="input-panel">
                        <h2>Your Resume</h2>
                        <textarea
                            value={resume}
                            onChange={(e) => setResume(e.target.value)}
                            placeholder="Paste your full resume text here..."
                        />
                    </div>
                    <div className="input-panel">
                        <h2>Job Description</h2>
                        <textarea
                            value={jobDescription}
                            onChange={(e) => setJobDescription(e.target.value)}
                            placeholder="Paste the target job description here..."
                        />
                    </div>
                    <div className="results-panel">
                        <div className="results-header">
                            <h2>Generated Cover Letter</h2>
                            <div className="results-actions">
                                <button onClick={handleCopy} disabled={!generatedCoverLetter || isLoading} className="btn btn-secondary">
                                    {copyButtonText}
                                </button>
                                {/* Added PDF Download button */}
                                <button onClick={handlePdfDownload} disabled={!generatedCoverLetter || isLoading} className="btn btn-secondary">
                                    Download PDF
                                </button>
                            </div>
                        </div>
                        <div className="results-content">
                            {isLoading && <div className="status-text">Generating cover letter...</div>}
                            {error && <div className="error-text">{error}</div>}
                            {generatedCoverLetter && <pre>{generatedCoverLetter}</pre>}
                            {!isLoading && !error && !generatedCoverLetter && (
                                <div className="placeholder-text">Your generated cover letter will appear here.</div>
                            )}
                        </div>
                    </div>
                </div>

                <div className="tailor-action">
                    <button className="btn btn-primary" onClick={handleGenerateCoverLetter} disabled={isLoading || !resume || !jobDescription}>
                        {isLoading ? 'Generating...' : 'Generate My Cover Letter'}
                    </button>
                </div>
            </div>

            <Footer />
        </div>
    );
};

export default CoverLetterGeneratorPage;