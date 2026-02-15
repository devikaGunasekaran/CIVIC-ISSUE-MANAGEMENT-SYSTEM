import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

function Signup() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSignup = async (e) => {
        e.preventDefault();
        try {
            await api.post('/auth/signup', {
                username,
                email,
                password
            });
            alert('Signup successful! Please login.');
            navigate('/login');
        } catch (error) {
            alert('Signup failed: ' + (error.response?.data?.detail || error.message));
        }
    };

    return (
        <div className="form-container glass-card animate-fade-in">
            <h2 className="form-title">Create Account</h2>
            <form onSubmit={handleSignup}>
                <div className="form-group">
                    <label className="form-label">Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label className="form-label">Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label className="form-label">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className="submit-btn primary">Sign Up</button>
            </form>
            <p style={{ marginTop: '20px', color: '#94a3b8' }}>
                Already have an account? <Link to="/login" className="login-link">Login</Link>
            </p>
        </div>
    );
}

export default Signup;
