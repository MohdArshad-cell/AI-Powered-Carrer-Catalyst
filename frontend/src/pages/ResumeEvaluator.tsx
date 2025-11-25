import React, { useState } from 'react';
import axios from 'axios';
import { saveAs } from 'file-saver';
import Navbar from '../components/Navbar';       // Assuming you have these components
import Footer from '../components/Footer';       // Assuming you have these components
import ParticleBackground from '../components/ParticleBackground'; // Assuming you have these components
import './AiTailorPage.css'; // You can reuse the same CSS file

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

const AtsEvaluatorPage: React.FC = () => {
    // Adapted state variables
    const [resumeText, setResumeText] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [evaluationResult, setEvaluationResult] = useState(''); // Changed from tailoredResume
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [copyButtonText, setCopyButtonText] = useState('Copy');

    // Adapted handler function
    const handleEvaluateResume = async () => {
        if (!resumeText || !jobDescription) {
            setError('Please provide both your resume and the job description.');
            return;
        }
        setIsLoading(true);
        setError('');
        setEvaluationResult('');
        setCopyButtonText('Copy');

        try {
            // NOTE: The payload keys `resume` and `jobDescription` must match your Spring Boot DTO
            const payload = { resume: resumeText, jobDescription: jobDescription };
            // NOTE: Using the correct API endpoint for the evaluator
            const response = await axios.post(`${API_BASE_URL}/api/v1/evaluate-resume`, payload);
            // NOTE: Using the correct response key `evaluation` from your backend
            setEvaluationResult(response.data.evaluation);
        } catch (err) {
            console.error("Error evaluating resume:", err);
            setError('Failed to get evaluation. The service may be down.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleTxtDownload = () => {
        // Saves the evaluation result
        const blob = new Blob([evaluationResult], { type: 'text/plain;charset=utf-8' });
        saveAs(blob, 'evaluation_report.txt'); // Changed filename
    };

    const handleCopy = () => {
        // Copies the evaluation result
        navigator.clipboard.writeText(evaluationResult).then(() => {
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
                    <h1>AI ATS Evaluator</h1>
                    <p>Get an instant analysis of your resume against any job description.</p>
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
                            <h2>Evaluation Report</h2>
                            <div className="results-actions">
                                <button onClick={handleCopy} disabled={!evaluationResult || isLoading} className="btn btn-secondary">
                                    {copyButtonText}
                                </button>
                                <button onClick={handleTxtDownload} disabled={!evaluationResult || isLoading} className="btn btn-secondary">
                                    Download TXT
                                </button>
                            </div>
                        </div>
                        <div className="results-content">
                            {isLoading && <div className="status-text">Generating report...</div>}
                            {error && <div className="error-text">{error}</div>}
                            {/* Using evaluationResult state and <pre> tag for formatting */}
                            {evaluationResult && <pre>{evaluationResult}</pre>}
                            {!isLoading && !error && !evaluationResult && (
                                <div className="placeholder-text">Your evaluation report will appear here.</div>
                            )}
                        </div>
                    </div>
                </div>

                <div className="tailor-action">
                    {/* Connects to the new handler */}
                    <button className="btn btn-primary" onClick={handleEvaluateResume} disabled={isLoading || !resumeText || !jobDescription}>
                        {isLoading ? 'Analyzing...' : 'Evaluate My Resume'}
                    </button>
                </div>
            </div>

            <Footer />
        </div>
    );
};

export default AtsEvaluatorPage;