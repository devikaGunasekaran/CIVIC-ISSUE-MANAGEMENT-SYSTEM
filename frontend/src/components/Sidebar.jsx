import { Link, useNavigate } from 'react-router-dom';
import { Home, FileText, MapPin, Bell, Info, LayoutDashboard, LogOut, Menu, X } from 'lucide-react';
import { useEffect, useState } from 'react';

function Sidebar() {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');
    const [isAdmin, setIsAdmin] = useState(false);
    const [isMobileOpen, setIsMobileOpen] = useState(false);

    useEffect(() => {
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setIsAdmin(payload.role === 'admin');
            } catch (error) {
                console.error('Error decoding token:', error);
            }
        } else {
            setIsAdmin(false);
        }
    }, [token]);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const NavItem = ({ to, icon: Icon, label, onClick }) => (
        <Link
            to={to}
            onClick={onClick}
            style={{
                display: 'flex',
                alignItems: 'center',
                gap: '15px',
                padding: '14px 20px',
                color: '#86efac',
                textDecoration: 'none',
                borderRadius: '12px',
                transition: 'all 0.2s',
                fontSize: '0.95rem',
                fontWeight: '500',
                marginBottom: '8px'
            }}
            onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(16, 185, 129, 0.15)';
                e.currentTarget.style.color = '#10b981';
                e.currentTarget.style.transform = 'translateX(5px)';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.color = '#86efac';
                e.currentTarget.style.transform = 'translateX(0)';
            }}
        >
            <Icon size={20} />
            <span>{label}</span>
        </Link>
    );

    const sidebarContent = (
        <>
            {/* Logo */}
            <div style={{
                padding: '30px 20px',
                borderBottom: '1px solid rgba(16, 185, 129, 0.2)',
                marginBottom: '20px'
            }}>
                <h1 style={{
                    fontSize: '1.8rem',
                    background: 'linear-gradient(135deg, #10b981, #34d399)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    fontWeight: '700',
                    margin: 0
                }}>
                    CivicApp
                </h1>
                <p style={{
                    color: '#6ee7b7',
                    fontSize: '0.85rem',
                    marginTop: '5px',
                    fontWeight: '500'
                }}>
                    {isAdmin ? 'Admin Panel' : 'Citizen Portal'}
                </p>
            </div>

            {/* Navigation */}
            <nav style={{ padding: '0 15px', flex: 1 }}>
                {token ? (
                    <>
                        <NavItem to="/" icon={Home} label="Home" onClick={() => setIsMobileOpen(false)} />

                        {!isAdmin && (
                            <>
                                <NavItem to="/report" icon={FileText} label="Report Issue" onClick={() => setIsMobileOpen(false)} />
                                <NavItem to="/track" icon={MapPin} label="Track" onClick={() => setIsMobileOpen(false)} />
                                <NavItem to="/notifications" icon={Bell} label="Notifications" onClick={() => setIsMobileOpen(false)} />
                            </>
                        )}

                        {isAdmin && (
                            <NavItem to="/admin" icon={LayoutDashboard} label="Admin Dashboard" onClick={() => setIsMobileOpen(false)} />
                        )}

                        <NavItem to="/about" icon={Info} label="About" onClick={() => setIsMobileOpen(false)} />
                    </>
                ) : (
                    <>
                        <NavItem to="/" icon={Home} label="Home" onClick={() => setIsMobileOpen(false)} />
                        <NavItem to="/about" icon={Info} label="About" onClick={() => setIsMobileOpen(false)} />
                    </>
                )}
            </nav>

            {/* Logout Button */}
            {token && (
                <div style={{ padding: '20px', borderTop: '1px solid rgba(16, 185, 129, 0.2)' }}>
                    <button
                        onClick={() => {
                            handleLogout();
                            setIsMobileOpen(false);
                        }}
                        style={{
                            width: '100%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '10px',
                            padding: '12px',
                            background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                            border: 'none',
                            borderRadius: '10px',
                            color: 'white',
                            fontSize: '0.95rem',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-2px)';
                            e.currentTarget.style.boxShadow = '0 8px 20px rgba(239, 68, 68, 0.4)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    >
                        <LogOut size={18} />
                        <span>Logout</span>
                    </button>
                </div>
            )}

            {!token && (
                <div style={{ padding: '20px', borderTop: '1px solid rgba(16, 185, 129, 0.2)' }}>
                    <Link to="/login">
                        <button
                            style={{
                                width: '100%',
                                padding: '12px',
                                background: 'linear-gradient(135deg, #10b981, #059669)',
                                border: 'none',
                                borderRadius: '10px',
                                color: 'white',
                                fontSize: '0.95rem',
                                fontWeight: '600',
                                cursor: 'pointer'
                            }}
                        >
                            Login
                        </button>
                    </Link>
                </div>
            )}
        </>
    );

    return (
        <>
            {/* Mobile Menu Button */}
            <button
                onClick={() => setIsMobileOpen(!isMobileOpen)}
                style={{
                    position: 'fixed',
                    top: '20px',
                    left: '20px',
                    zIndex: 1100,
                    display: 'none',
                    background: 'linear-gradient(135deg, #10b981, #059669)',
                    border: 'none',
                    borderRadius: '10px',
                    padding: '10px',
                    color: 'white',
                    cursor: 'pointer'
                }}
                className="mobile-menu-btn"
            >
                {isMobileOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            <style>{`
                @media (max-width: 768px) {
                    .mobile-menu-btn {
                        display: block !important;
                    }
                }
            `}</style>

            {/* Desktop Sidebar */}
            <div
                style={{
                    position: 'fixed',
                    left: 0,
                    top: 0,
                    width: '280px',
                    height: '100vh',
                    background: 'linear-gradient(180deg, #0f2f27 0%, #0a1f1a 100%)',
                    borderRight: '1px solid rgba(16, 185, 129, 0.2)',
                    display: 'flex',
                    flexDirection: 'column',
                    zIndex: 1000,
                    transition: 'transform 0.3s ease',
                    transform: isMobileOpen ? 'translateX(0)' : 'translateX(0)'
                }}
                className="sidebar-desktop"
            >
                {sidebarContent}
            </div>

            {/* Mobile Sidebar */}
            <div
                style={{
                    position: 'fixed',
                    left: 0,
                    top: 0,
                    width: '280px',
                    height: '100vh',
                    background: 'linear-gradient(180deg, #0f2f27 0%, #0a1f1a 100%)',
                    borderRight: '1px solid rgba(16, 185, 129, 0.2)',
                    display: 'none',
                    flexDirection: 'column',
                    zIndex: 1000,
                    transition: 'transform 0.3s ease',
                    transform: isMobileOpen ? 'translateX(0)' : 'translateX(-100%)'
                }}
                className="sidebar-mobile"
            >
                {sidebarContent}
            </div>

            {/* Mobile Overlay */}
            {isMobileOpen && (
                <div
                    onClick={() => setIsMobileOpen(false)}
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'rgba(0, 0, 0, 0.7)',
                        zIndex: 999,
                        display: 'none'
                    }}
                    className="mobile-overlay"
                />
            )}

            <style>{`
                @media (max-width: 768px) {
                    .sidebar-desktop {
                        display: none !important;
                    }
                    .sidebar-mobile {
                        display: flex !important;
                    }
                    .mobile-overlay {
                        display: block !important;
                    }
                }
            `}</style>
        </>
    );
}

export default Sidebar;
