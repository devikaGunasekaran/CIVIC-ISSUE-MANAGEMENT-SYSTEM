import { useTranslation } from 'react-i18next';
import { Info, Target, Shield, Mail, Phone, Clock } from 'lucide-react';

function AboutPage() {
    const { t } = useTranslation();
    return (
        <div className="max-w-4xl mx-auto py-16 px-8 space-y-12 animate-fade-in-up bg-white min-h-screen">
            <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-gray-50 rounded-2xl flex items-center justify-center text-primary shadow-sm border border-gray-100">
                    <Info size={24} />
                </div>
                <div className="space-y-1">
                    <h2 className="text-4xl font-extrabold text-secondary tracking-tight">
                        {t('about.title')}
                    </h2>
                    <p className="text-secondary/60 text-sm font-medium">Empowering citizens through intelligent urban management</p>
                </div>
            </div>

            <div className="grid gap-8">
                <section className="bg-white p-8 rounded-3xl border border-gray-100 shadow-soft space-y-4">
                    <div className="flex items-center gap-3 text-primary mb-2">
                        <Target size={20} />
                        <h3 className="text-xl font-bold text-secondary">{t('about.feature1Title')}</h3>
                    </div>
                    <p className="text-secondary/70 leading-relaxed font-medium">{t('about.feature1Desc')}</p>
                </section>

                <section className="bg-white p-8 rounded-3xl border border-gray-100 shadow-soft space-y-4">
                    <div className="flex items-center gap-3 text-primary mb-2">
                        <Shield size={20} />
                        <h3 className="text-xl font-bold text-secondary">{t('about.feature2Title')}</h3>
                    </div>
                    <p className="text-secondary/70 leading-relaxed font-medium">{t('about.feature2Desc')}</p>
                </section>

                <section className="bg-white p-8 rounded-3xl border border-gray-100 shadow-soft space-y-4">
                    <div className="flex items-center gap-3 text-primary mb-2">
                        <Info size={20} />
                        <h3 className="text-xl font-bold text-secondary">{t('about.feature3Title')}</h3>
                    </div>
                    <p className="text-secondary/70 leading-relaxed font-medium">{t('about.feature3Desc')}</p>
                </section>

                <section className="bg-primary/5 p-8 rounded-3xl border border-primary/10 space-y-6">
                    <h3 className="text-xl font-bold text-secondary flex items-center gap-3">
                        Contact Official Support
                    </h3>
                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-primary shadow-sm">
                                <Clock size={18} />
                            </div>
                            <div>
                                <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Availability</p>
                                <p className="text-sm font-bold text-secondary">Mon-Fri, 9am - 5pm</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-primary shadow-sm">
                                <Mail size={18} />
                            </div>
                            <div>
                                <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Email</p>
                                <a href="mailto:support@civicapp.com" className="text-sm font-bold text-primary hover:underline">support@civicapp.com</a>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-primary shadow-sm">
                                <Phone size={18} />
                            </div>
                            <div>
                                <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Phone</p>
                                <p className="text-sm font-bold text-secondary">+1 234 567 890</p>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
}

export default AboutPage;
