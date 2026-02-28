import { Link, useNavigate } from 'react-router-dom';
import { Home, PlusCircle, LayoutList, Bell, Info, LogOut, Shield, Zap } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';

function Navbar() {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');
    const [isAdmin, setIsAdmin] = useState(false);
    const { t } = useTranslation();

    useEffect(() => {
        if (token) {
            try {
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
        <nav className="bg-white border-b border-gray-100 sticky top-0 z-50 px-8 py-4 flex justify-between items-center shadow-sm">
            <Link to="/" className="flex items-center gap-2 group">
                <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white shadow-lg shadow-green-100 group-hover:scale-105 transition-transform">
                    <Zap size={20} fill="currentColor" />
                </div>
                <span className="text-2xl font-black text-secondary tracking-tighter">
                    {t('nav.brand')}
                </span>
            </Link>

            <div className="flex items-center gap-8">
                <div className="hidden md:flex items-center gap-10">
                    <CustomNavLink to="/" icon={<Home size={18} />} label={t('nav.home')} />

                    {!isAdmin && token && (
                        <>
                            <CustomNavLink to="/report" icon={<PlusCircle size={18} />} label={t('nav.reportIssue')} />
                            <CustomNavLink to="/track" icon={<LayoutList size={18} />} label={t('nav.track')} />
                        </>
                    )}

                    <CustomNavLink to="/about" icon={<Info size={18} />} label={t('nav.about')} />

                    {isAdmin && (
                        <CustomNavLink to="/admin" icon={<Shield size={18} />} label={t('nav.admin')} />
                    )}
                </div>

                <div className="flex items-center gap-6 pl-8 border-l border-gray-100">
                    {token ? (
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 text-gray-400 hover:text-red-500 font-bold transition-colors text-xs uppercase tracking-widest"
                        >
                            <LogOut size={16} />
                            <span className="hidden sm:inline">{t('nav.logout')}</span>
                        </button>
                    ) : (
                        <Link
                            to="/login"
                            className="text-xs font-black uppercase tracking-widest text-primary hover:text-secondary transition-colors"
                        >
                            {t('nav.login')}
                        </Link>
                    )}
                    <LanguageSelector />
                </div>
            </div>
        </nav>
    );
}

function CustomNavLink({ to, icon, label }) {
    return (
        <Link
            to={to}
            className="flex items-center gap-2 text-secondary/60 hover:text-primary font-bold transition-all group relative py-2"
        >
            <span className="group-hover:scale-110 transition-transform opacity-70 group-hover:opacity-100">{icon}</span>
            <span className="text-[10px] uppercase tracking-[0.2em]">{label}</span>
            <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-primary transition-all group-hover:w-full"></span>
        </Link>
    );
}

export default Navbar;
