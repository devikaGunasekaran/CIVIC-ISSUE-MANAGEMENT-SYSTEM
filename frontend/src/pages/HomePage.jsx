import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowRight, Shield, Zap, BarChart3, Clock, CheckCircle2, Facebook, Phone } from 'lucide-react';
import api from '../api';

function HomePage() {
    const { t } = useTranslation();
    const navigate = useNavigate();

    // Using the generated image path
    const heroImage = "/hero_civic_clean_illustration_1772122071678.png";

    const handleSocialLogin = async (provider) => {
        try {
            // Mock social login data
            const socialData = {
                email: provider === 'phone' ? null : `citizen_${Math.floor(Math.random() * 1000)}@${provider}.local`,
                phone: provider === 'phone' ? `+91 ${Math.floor(1000000000 + Math.random() * 9000000000)}` : null,
                name: "Real-Time Citizen",
                provider: provider
            };

            const response = await api.post('/auth/social-login', socialData);
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                // Instant redirect to report for "Real-Time" experience
                navigate('/report');
                window.location.reload(); // Refresh to update sidebar/navbar state
            }
        } catch (error) {
            console.error('Social login failed:', error);
            navigate('/login');
        }
    };

    return (
        <div className="bg-white">
            {/* Hero Section */}
            <section className="relative overflow-hidden pt-20 pb-28 lg:pt-32 lg:pb-40 px-8">
                <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-20 items-center">
                    <div className="space-y-8 animate-fade-in-up">
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-50 border border-green-100 rounded-full text-primary font-bold text-xs uppercase tracking-widest">
                            <Zap size={14} />
                            {t('home.aiGovernance')}
                        </div>
                        <h1 className="text-4xl lg:text-6xl font-extrabold text-secondary leading-[1.15] tracking-tight">
                            {t('home.title')}
                        </h1>
                        <p className="text-lg text-secondary/60 leading-relaxed max-w-xl">
                            {t('home.subtitle')}
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 pt-4 text-center">
                            <Link to="/report" className="btn-primary flex items-center justify-center gap-2 group">
                                {t('home.reportIssue')}
                                <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                            </Link>
                            <Link to="/track" className="btn-outline">
                                {t('home.trackStatus')}
                            </Link>
                        </div>

                        {/* Real-Time Access Widget */}
                        <div className="pt-6">
                            <div className="bg-gray-50 border border-gray-100 rounded-3xl p-6 shadow-soft max-w-md">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center text-primary">
                                        <Zap size={18} />
                                    </div>
                                    <span className="text-xs font-black uppercase tracking-widest text-secondary/70">{t('home.realTimeAccess')}</span>
                                </div>
                                <div className="space-y-4">
                                    <p className="text-sm font-medium text-secondary/60">{t('home.oneClickLogin')}</p>
                                    <button
                                        onClick={() => handleSocialLogin('google')}
                                        className="w-full flex items-center justify-center gap-3 h-12 bg-white border border-gray-100 rounded-xl hover:bg-gray-50 transition-all shadow-sm group"
                                    >
                                        <svg className="w-5 h-5 group-hover:scale-110 transition-transform" viewBox="0 0 24 24">
                                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" />
                                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                                        </svg>
                                        <span className="text-[10px] font-black uppercase tracking-[0.1em] text-secondary">Google</span>
                                    </button>
                                    <div className="grid grid-cols-2 gap-3">
                                        <button
                                            onClick={() => handleSocialLogin('facebook')}
                                            className="w-full flex items-center justify-center gap-3 h-12 bg-white border border-gray-100 rounded-xl hover:bg-gray-50 transition-all shadow-sm group"
                                        >
                                            <Facebook size={16} className="text-[#1877F2] group-hover:scale-110 transition-transform" />
                                            <span className="text-[10px] font-black uppercase tracking-[0.1em] text-secondary">Facebook</span>
                                        </button>
                                        <button
                                            onClick={() => handleSocialLogin('phone')}
                                            className="w-full flex items-center justify-center gap-3 h-12 bg-white border border-gray-100 rounded-xl hover:bg-gray-50 transition-all shadow-sm group"
                                        >
                                            <Phone size={16} className="text-primary group-hover:scale-110 transition-transform" />
                                            <span className="text-[10px] font-black uppercase tracking-[0.1em] text-secondary">Phone</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="relative animate-fade-in-up flex items-center justify-center p-4 lg:p-0" style={{ animationDelay: '0.2s' }}>
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-primary/5 rounded-full blur-[100px] opacity-40"></div>
                        <div className="relative w-full max-w-[600px] h-auto transform hover:scale-[1.02] transition-transform duration-700">
                            <img
                                src={heroImage}
                                alt="Dashboard Visual"
                                className="w-full h-auto drop-shadow-2xl"
                            />
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="bg-white/50 py-24 px-6 border-y border-earth/10">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
                        <h2 className="text-3xl font-bold text-secondary tracking-tight">{t('home.advancedFeatures')}</h2>
                        <p className="text-earth/70 font-medium italic">{t('home.featuresDesc')}</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        <FeatureCard
                            icon={<Zap className="text-orange-500" />}
                            title={t('home.easyReporting')}
                            description={t('home.easyReportingDesc')}
                        />
                        <FeatureCard
                            icon={<BarChart3 className="text-blue-500" />}
                            title={t('home.realTimeUpdates')}
                            description={t('home.realTimeUpdatesDesc')}
                        />
                        <FeatureCard
                            icon={<Shield className="text-primary" />}
                            title={t('home.aiPowered')}
                            description={t('home.aiPoweredDesc')}
                        />
                    </div>
                </div>
            </section>

            {/* How it Works */}
            <section className="py-24 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="flex flex-col md:flex-row gap-12 items-center">
                        <div className="md:w-1/2 space-y-6">
                            <h2 className="text-4xl font-bold text-secondary tracking-tight leading-tight">
                                {t('home.streamlinedWorkflow')}
                            </h2>
                            <p className="text-gray-500 text-lg">
                                {t('home.workflowDesc')}
                            </p>
                            <div className="space-y-8 pt-4">
                                <div className="flex gap-6 items-start">
                                    <div className="w-12 h-12 shrink-0 rounded-2xl flex items-center justify-center font-bold text-lg bg-gray-100 text-gray-600">
                                        01
                                    </div>
                                    <div className="space-y-1">
                                        <h4 className="text-xl font-bold text-secondary">{t('home.step1Title')}</h4>
                                        <p className="text-gray-500">{t('home.step1Desc')}</p>
                                    </div>
                                </div>
                                <div className="flex gap-6 items-start">
                                    <div className="w-12 h-12 shrink-0 rounded-2xl flex items-center justify-center font-bold text-lg bg-gray-100 text-gray-600">
                                        02
                                    </div>
                                    <div className="space-y-1">
                                        <h4 className="text-xl font-bold text-secondary">{t('home.step2Title')}</h4>
                                        <p className="text-gray-500">{t('home.step2Desc')}</p>
                                    </div>
                                </div>
                                <div className="flex gap-6 items-start">
                                    <div className="w-12 h-12 shrink-0 rounded-2xl flex items-center justify-center font-bold text-lg bg-primary text-white shadow-lg shadow-green-200">
                                        03
                                    </div>
                                    <div className="space-y-1">
                                        <h4 className="text-xl font-bold text-secondary">{t('home.step3Title')}</h4>
                                        <p className="text-gray-500">{t('home.step3Desc')}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="md:w-1/2">
                            <div className="bg-gray-50 rounded-3xl p-8 border border-gray-100 shadow-inner">
                                <div className="space-y-4">
                                    <div className="bg-white p-4 rounded-xl shadow-soft border border-green-50 flex items-center gap-4">
                                        <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center text-primary font-bold">1</div>
                                        <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                                            <div className="w-full h-full bg-primary animate-pulse"></div>
                                        </div>
                                        <CheckCircle2 size={24} className="text-primary" />
                                    </div>
                                    <div className="bg-white p-4 rounded-xl shadow-soft border border-green-50 scale-95 opacity-80 flex items-center gap-4">
                                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold">2</div>
                                        <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                                            <div className="w-1/2 h-full bg-blue-500"></div>
                                        </div>
                                        <Clock size={24} className="text-blue-500" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="max-w-7xl mx-auto px-6 mb-24">
                <div className="bg-gradient-to-r from-primary to-earth rounded-[2.5rem] p-12 text-center text-white space-y-8 shadow-premium overflow-hidden relative">
                    <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-accent/20 rounded-full blur-3xl"></div>
                    <div className="relative z-10 space-y-4">
                        <h2 className="text-4xl font-bold">{t('home.ctaTitle')}</h2>
                        <p className="text-accent/80 max-w-xl mx-auto italic">{t('home.ctaSubtitle')}</p>
                        <div className="pt-4">
                            <Link to="/report" className="px-10 py-4 bg-white text-primary font-bold rounded-2xl hover:bg-accent transition-all inline-block shadow-soft">
                                {t('home.ctaButton')}
                            </Link>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}

function FeatureCard({ icon, title, description }) {
    return (
        <div className="glass-card hover:-translate-y-2 group">
            <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center mb-6 group-hover:bg-white transition-colors duration-300">
                {icon}
            </div>
            <h3 className="text-xl font-bold text-secondary mb-3">{title}</h3>
            <p className="text-gray-500 leading-relaxed text-sm">
                {description}
            </p>
        </div>
    );
}

export default HomePage;
