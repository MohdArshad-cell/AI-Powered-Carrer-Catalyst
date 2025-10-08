import React from 'react';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();

    const launchTools = () => {
        // This can be adjusted based on the page, but for now, it goes to the builder
        navigate('/ai-tools');
    };

    return (
        <nav className="navbar">
            <div className="container nav-container">
                {/* Clicking the logo will always take the user to the homepage */}
                <a href="/" className="nav-logo">Career Catalyst</a>
                <div className="nav-links">
                    <a href="/#full-bento-grid">Features</a>
                    <a href="/#footer">Contact</a>
                    <button onClick={launchTools} className="btn btn-outline nav-cta">
                        Launch App
                    </button>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;