import React, { useState } from 'react';
import axios from 'axios';
import { saveAs } from 'file-saver'; // Make sure to install this: npm install file-saver
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ParticleBackground from '../components/ParticleBackground';
import './AiTailorPage.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

const AiTailorPage: React.FC = () => {
    const [resumeText, setResumeText] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [tailoredResume, setTailoredResume] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [copyButtonText, setCopyButtonText] = useState('Copy');

    const handleTailorResume = async () => {
        if (!resumeText || !jobDescription) {
            setError('Please provide both your resume and the job description.');
            return;
        }
        setIsLoading(true);
        setError('');
        setTailoredResume('');
        setCopyButtonText('Copy');

        try {
            const payload = { resumeText, jobDescription };
            const response = await axios.post(`${API_BASE_URL}/api/v1/tailor`, payload);
            setTailoredResume(response.data.tailoredResume);
        } catch (err) {
            console.error("Error tailoring resume:", err);
            setError('Failed to get AI suggestions. The service may be down.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleTxtDownload = () => {
        const blob = new Blob([tailoredResume], { type: 'text/plain;charset=utf-8' });
        saveAs(blob, 'tailored_resume.txt');
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(tailoredResume).then(() => {
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
                    <h1>AI Resume Tailor</h1>
                    <p>Instantly optimize your resume for any job description with AI.</p>
                </div>

                <div className="tailor-grid">
                    <div className="input-panel">
                        <h2>Your Resume</h2>
                        <textarea
                            value={resumeText}
                            onChange={(e) => setResumeText(e.target.value)}
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
                            <h2>AI Suggestions</h2>
                            <div className="results-actions">
                                <button onClick={handleCopy} disabled={!tailoredResume || isLoading} className="btn btn-secondary">
                                    {copyButtonText}
                                </button>
                                <button onClick={handleTxtDownload} disabled={!tailoredResume || isLoading} className="btn btn-secondary">
                                    Download TXT
                                </button>
                            </div>
                        </div>
                        <div className="results-content">
                            {isLoading && <div className="status-text">Generating suggestions...</div>}
                            {error && <div className="error-text">{error}</div>}
                            {tailoredResume && <pre>{tailoredResume}</pre>}
                            {!isLoading && !error && !tailoredResume && (
                                <div className="placeholder-text">Your tailored resume will appear here.</div>
                            )}
                        </div>
                    </div>
                </div>

                <div className="tailor-action">
                    <button className="btn btn-primary" onClick={handleTailorResume} disabled={isLoading || !resumeText || !jobDescription}>
                        {isLoading ? 'Analyzing...' : 'Tailor My Resume'}
                    </button>
                </div>
            </div>

            <Footer />
        </div>
    );
};

export default AiTailorPage;