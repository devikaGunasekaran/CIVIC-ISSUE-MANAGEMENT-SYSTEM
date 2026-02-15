import { Link, useNavigate } from 'react-router-dom';
import { Home, PlusCircle, LayoutList, Bell, Info, LogOut, Shield } from 'lucide-react';
import { useState, useEffect } from 'react';

function Navbar() {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        if (token) {
            try {
                // Decode JWT token to check role
                const payload = JSON.parse(atob(token.split('.')[1]));
                setIsAdmin(payload.role === 'admin' || payload.role === 'area_admin');
            } catch (error) {
                console.error('Error decoding token:', error);
            }
        } else {
            setIsAdmin(false);
        }
    }, [token]);

    const handleLogout = () => {
        localStorage.removeItem('token');
        setIsAdmin(false);
        navigate('/login');
    };

    return (
        <nav style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '20px 40px',
            background: 'rgba(15, 23, 42, 0.8)',
            backdropFilter: 'blur(10px)',
            borderBottom: '1px solid rgba(255,255,255,0.1)',
            position: 'sticky',
            top: 0,
            zIndex: 100
        }}>
            <Link to="/" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white', textDecoration: 'none', background: 'linear-gradient(to right, #6366f1, #a855f7)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Civic<span style={{ color: 'white' }}>App</span>
            </Link>

            <div style={{ display: 'flex', gap: '30px' }}>
                <NavLink to="/" icon={<Home size={20} />} label="Home" />

                {/* Citizen-only links */}
                {!isAdmin && token && (
                    <>
                        <NavLink to="/report" icon={<PlusCircle size={20} />} label="Report Issue" />
                        <NavLink to="/track" icon={<LayoutList size={20} />} label="Track" />
                        <NavLink to="/notifications" icon={<Bell size={20} />} label="Notifications" />
                    </>
                )}

                <NavLink to="/about" icon={<Info size={20} />} label="About" />

                {/* Admin-only link */}
                {isAdmin && (
                    <NavLink to="/admin" icon={<Shield size={20} />} label="Admin Dashboard" />
                )}

                {token && (
                    <button onClick={handleLogout} style={{ background: 'transparent', border: 'none', color: '#cbd5e1', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}>
                        <LogOut size={20} /> Logout
                    </button>
                )}
                {!token && (
                    <Link to="/login" style={{ color: '#cbd5e1', textDecoration: 'none', fontWeight: 'bold' }}>Login</Link>
                )}
            </div>
        </nav>
    );
}

function NavLink({ to, icon, label }) {
    return (
        <Link to={to} style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#cbd5e1', textDecoration: 'none', transition: 'color 0.2s' }}>
            {icon}
            <span style={{ fontSize: '0.9rem' }}>{label}</span>
            <style>{`
        a:hover { color: #a855f7 !important; }
      `}</style>
        </Link>
    );
}

export default Navbar;
