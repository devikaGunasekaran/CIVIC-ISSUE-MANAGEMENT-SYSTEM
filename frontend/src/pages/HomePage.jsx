import { Link } from 'react-router-dom';

function HomePage() {
    return (
        <div className="home-container">
            <header className="hero-header glass-card animate-fade-in">
                <h1 className="hero-title">Civic Issue Management</h1>
                <p className="hero-subtitle">
                    Empowering citizens to report and resolve civic problems seamlessly.
                </p>
                <div className="action-buttons">
                    <Link to="/report" className="cta-button primary">
                        📢 Report Issue
                    </Link>
                    <Link to="/track" className="cta-button secondary">
                        🔍 Track Status
                    </Link>
                </div>
            </header>

            <div className="features-grid">
                <div className="feature-card glass-card">
                    <h3>Easy Reporting</h3>
                    <p>Quickly report issues with location and images.</p>
                </div>
                <div className="feature-card glass-card">
                    <h3>Real-time Updates</h3>
                    <p>Track the progress of your complaint anytime.</p>
                </div>
                <div className="feature-card glass-card">
                    <h3>AI Powered</h3>
                    <p>Smart categorization for faster resolution.</p>
                </div>
            </div>

            <br />
            <div className="admin-access">
                <Link to="/login" className="login-link">Login / Admin Access</Link>
            </div>
        </div>
    );
}

export default HomePage;
