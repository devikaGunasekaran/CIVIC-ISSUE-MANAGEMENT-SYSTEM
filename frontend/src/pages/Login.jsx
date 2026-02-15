import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await api.post('/auth/token', formData);
            const token = response.data.access_token;
            localStorage.setItem('token', token);

            // Decode JWT to get user role
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                console.log('Decoded token payload:', payload);
                const userRole = payload.role;
                console.log('User role:', userRole);

                alert(`Login successful! Welcome ${userRole === 'admin' ? 'Admin' : 'Citizen'}!`);

                // Redirect based on role
                if (userRole === 'admin' || userRole === 'area_admin') {
                    console.log('Redirecting to admin dashboard');
                    navigate('/admin');
                } else {
                    console.log('Redirecting to tracking page');
                    navigate('/report-issue'); // Better UX for citizen
                }
            } catch (decodeError) {
                console.error('Error decoding token:', decodeError);
                alert('Login successful but could not determine user role. Redirecting to home.');
                navigate('/');
            }
        } catch (error) {
            alert('Login failed: ' + (error.response?.data?.detail || error.message));
        }
    };

    return (
        <div className="form-container glass-card animate-fade-in">
            <h2 className="form-title">Login</h2>
            <form onSubmit={handleLogin}>
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
                    <label className="form-label">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className="submit-btn">Login</button>
            </form>
            <p style={{ marginTop: '20px', color: '#94a3b8' }}>
                Don't have an account? <Link to="/signup" className="login-link">Sign up</Link>
            </p>
        </div>
    );
}

export default Login;
