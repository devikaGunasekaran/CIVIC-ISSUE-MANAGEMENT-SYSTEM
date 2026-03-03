import { Link, useNavigate } from 'react-router-dom';
import { Home, FileText, MapPin, Bell, Info, LayoutDashboard, LogOut, Menu, X, User } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';

function Sidebar() {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');
    const [isAdmin, setIsAdmin] = useState(false);
    const [username, setUsername] = useState(null);
    const [isMobileOpen, setIsMobileOpen] = useState(false);
    const { t } = useTranslation();

    useEffect(() => {
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setIsAdmin(payload.role === 'admin' || payload.role === 'area_admin');
                setUsername(payload.sub);
            } catch (error) {
                console.error('Error decoding token:', error);
            }
        } else {
            setIsAdmin(false);
            setUsername(null);
        }
    }, [token]);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const NavItem = ({ to, icon: Icon, label, onClick }) => {
        const isActive = location.pathname === to;
        return (
            <Link
                to={to}
                onClick={onClick}
                className={`flex items-center gap-4 px-5 py-3 rounded-xl transition-all duration-200 font-semibold group ${isActive
                    ? 'bg-primary text-white shadow-md'
                    : 'text-secondary/70 hover:text-primary hover:bg-primary/5'
                    }`}
            >
                <Icon size={20} className={`${isActive ? '' : 'group-hover:scale-110'} transition-transform`} />
                <span className="text-[0.9rem]">{label}</span>
            </Link>
        );
    };

    const sidebarContent = (
        <div className="flex flex-col h-full bg-mint">
            {/* Logo */}
            <div className="p-8 border-b border-primary/10 mb-6">
                <Link to="/" onClick={() => setIsMobileOpen(false)} className="block">
                    <h1 className="text-2xl font-bold text-primary tracking-tight">
                        CivicApp
                    </h1>
                </Link>
                <p className="text-secondary/50 text-[0.65rem] uppercase font-bold tracking-[2px] mt-1">
                    {isAdmin ? t('sidebar.adminPanel') : t('sidebar.citizenPortal')}
                </p>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 space-y-1">
                {token ? (
                    <>
                        <NavItem to="/" icon={Home} label={t('nav.home')} onClick={() => setIsMobileOpen(false)} />

                        {!isAdmin && (
                            <>
                                <NavItem to="/report" icon={FileText} label={t('nav.reportIssue')} onClick={() => setIsMobileOpen(false)} />
                                <NavItem to="/track" icon={MapPin} label={t('nav.track')} onClick={() => setIsMobileOpen(false)} />
                                <NavItem to="/notifications" icon={Bell} label={t('nav.notifications')} onClick={() => setIsMobileOpen(false)} />
                            </>
                        )}

                        {isAdmin && (
                            <NavItem to="/admin" icon={LayoutDashboard} label={t('nav.admin')} onClick={() => setIsMobileOpen(false)} />
                        )}

                        <NavItem to="/about" icon={Info} label={t('nav.about')} onClick={() => setIsMobileOpen(false)} />
                    </>
                ) : (
                    <>
                        <NavItem to="/" icon={Home} label={t('nav.home')} onClick={() => setIsMobileOpen(false)} />
                        <NavItem to="/about" icon={Info} label={t('nav.about')} onClick={() => setIsMobileOpen(false)} />
                    </>
                )}
            </nav>

            {/* Footer Section */}
            <div className="p-6 border-t border-earth/5 space-y-4">
                <LanguageSelector />

                {token && username && (
                    <div className="flex items-center gap-4 p-4 mb-2 bg-primary/5 rounded-2xl border border-primary/10">
                        <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center text-primary">
                            <User size={20} />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-[10px] uppercase tracking-widest font-bold text-secondary/40 leading-none mb-1">
                                {t('sidebar.loggedInAs')}
                            </p>
                            <p className="text-sm font-black text-secondary truncate">
                                {username}
                            </p>
                        </div>
                    </div>
                )}

                {token ? (
                    <button
                        onClick={() => {
                            handleLogout();
                            setIsMobileOpen(false);
                        }}
                        className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-xl text-red-600 font-semibold border-2 border-red-100 hover:bg-red-50 hover:border-red-200 transition-all"
                    >
                        <LogOut size={18} />
                        <span>{t('nav.logout')}</span>
                    </button>
                ) : (
                    <Link to="/login" onClick={() => setIsMobileOpen(false)}>
                        <button className="btn-primary w-full">
                            {t('nav.login')}
                        </button>
                    </Link>
                )}
            </div>
        </div>
    );

    return (
        <>
            {/* Mobile Toggle */}
            <button
                onClick={() => setIsMobileOpen(!isMobileOpen)}
                className="fixed top-4 left-4 z-[60] md:hidden p-3 rounded-xl bg-primary text-white shadow-lg hover:scale-105 active:scale-95 transition-all"
            >
                {isMobileOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            {/* Backdrop */}
            {isMobileOpen && (
                <div
                    onClick={() => setIsMobileOpen(false)}
                    className="fixed inset-0 bg-secondary/40 backdrop-blur-sm z-[45] md:hidden transition-opacity"
                />
            )}

            {/* Sidebar Container */}
            <aside
                className={`fixed top-0 left-0 h-full w-[260px] bg-mint border-r border-primary/5 z-50 transition-transform duration-300 md:translate-x-0 ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'
                    }`}
            >
                {sidebarContent}
            </aside>

            {/* Main Content Spacer for fixed sidebar */}
            <div className="hidden md:block w-[260px] shrink-0" />
        </>
    );
}

export default Sidebar;
