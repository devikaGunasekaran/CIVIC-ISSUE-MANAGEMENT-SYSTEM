import { Link } from 'react-router-dom';
import { Mail, Phone, MapPin, ShieldCheck, Zap } from 'lucide-react';
import { useTranslation } from 'react-i18next';

function Footer() {
    const { t } = useTranslation();
    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-gray-50 border-t border-gray-100 pt-20 pb-10 px-8">
            <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-16 mb-16">
                {/* Brand & Mission */}
                <div className="space-y-6">
                    <div className="flex items-center gap-2 group">
                        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white shadow-lg shadow-green-100">
                            <Zap size={20} fill="currentColor" />
                        </div>
                        <span className="text-2xl font-black text-secondary tracking-tighter">CivicApp</span>
                    </div>
                    <p className="text-secondary/50 text-sm leading-relaxed font-medium">
                        Dedicated AI-powered infrastructure for efficient civic issue management and smart city governance.
                    </p>
                </div>

                {/* Quick Links */}
                <div className="md:ml-auto">
                    <h4 className="text-secondary font-black mb-8 uppercase text-[10px] tracking-[0.2em] opacity-40">{t('footer.quickLinks', { defaultValue: 'Quick Links' })}</h4>
                    <ul className="space-y-4">
                        <li><Link to="/" className="text-secondary/60 hover:text-primary transition-colors text-sm font-bold">{t('nav.home')}</Link></li>
                        <li><Link to="/report" className="text-secondary/60 hover:text-primary transition-colors text-sm font-bold">{t('nav.reportIssue')}</Link></li>
                        <li><Link to="/track" className="text-secondary/60 hover:text-primary transition-colors text-sm font-bold">{t('nav.track')}</Link></li>
                        <li><Link to="/about" className="text-secondary/60 hover:text-primary transition-colors text-sm font-bold">{t('nav.about')}</Link></li>
                    </ul>
                </div>

                {/* Government Sections */}
                <div className="md:ml-auto">
                    <h4 className="text-secondary font-black mb-8 uppercase text-[10px] tracking-[0.2em] opacity-40">{t('footer.government', { defaultValue: 'Government' })}</h4>
                    <ul className="space-y-4">
                        <li><a href="#" className="text-secondary/60 hover:text-primary transition-colors text-sm font-bold">City Corporation</a></li>
                        <li><a href="#" className="text-secondary/60 hover:text-primary transition-colors text-sm font-bold">Public Works Dept</a></li>
                        <li><a href="#" className="text-secondary/60 hover:text-primary transition-colors text-sm font-bold">Urban Development</a></li>
                    </ul>
                </div>

                {/* Contact Info */}
                <div className="md:ml-auto">
                    <h4 className="text-secondary font-black mb-8 uppercase text-[10px] tracking-[0.2em] opacity-40">{t('footer.contact', { defaultValue: 'Contact Support' })}</h4>
                    <div className="space-y-6">
                        <div className="flex items-center gap-4 text-secondary/60">
                            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-primary shadow-sm">
                                <Mail size={16} />
                            </div>
                            <span className="text-sm font-bold">support@civicapp.gov.in</span>
                        </div>
                        <div className="flex items-center gap-4 text-secondary/60">
                            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-primary shadow-sm">
                                <Phone size={16} />
                            </div>
                            <span className="text-sm font-bold">1800-425-XXXX</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="max-w-7xl mx-auto pt-10 border-t border-gray-100 flex flex-col md:flex-row justify-between items-center gap-6 text-gray-400 text-[10px] font-black uppercase tracking-widest">
                <p>© {currentYear} Civic Issue Management System. All rights reserved.</p>
                <div className="flex items-center gap-8">
                    <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
                    <a href="#" className="hover:text-primary transition-colors">Terms of Service</a>
                </div>
            </div>
        </footer>
    );
}

export default Footer;
