import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import api from '../api';
import LanguageSelector from '../components/LanguageSelector';
import { ShieldCheck, Mail, Lock, ArrowRight, User, Phone, Facebook } from 'lucide-react';

function Signup() {
    const [username, setUsername] = React.useState('');
    const [email, setEmail] = React.useState('');
    const [password, setPassword] = React.useState('');
    const [signupMode, setSignupMode] = React.useState('standard'); // 'standard', 'phone'
    const [phoneNumber, setPhoneNumber] = React.useState('');
    const [otp, setOtp] = React.useState('');
    const [isOtpSent, setIsOtpSent] = React.useState(false);
    const navigate = useNavigate();
    const { t } = useTranslation();

    const handleSocialLogin = async (provider, emailPayload = null) => {
        try {
            const socialData = {
                email: emailPayload || `user_${Math.floor(Math.random() * 1000)}@${provider}.local`,
                name: emailPayload ? emailPayload.split('@')[0] : `Social ${provider} User`,
                provider: provider
            };

            const response = await api.post('/auth/social-login', socialData);
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                navigate('/report');
                window.location.reload();
            }
        } catch (error) {
            console.error(`${provider} signup failed:`, error);
        }
    };

    const handlePhoneSignup = async (e) => {
        e.preventDefault();
        if (!isOtpSent) {
            setIsOtpSent(true);
            return;
        }

        try {
            const socialData = {
                phone: phoneNumber,
                provider: 'phone',
                otp: otp
            };

            const response = await api.post('/auth/social-login', socialData);
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                navigate('/report');
                window.location.reload();
            }
        } catch (error) {
            console.error('Phone signup failed:', error);
        }
    };

    const handleSignup = async (e) => {
        e.preventDefault();
        try {
            await api.post('/auth/signup', { username, email, password });
            navigate('/login');
        } catch (error) {
            console.error('Signup failed:', error);
        }
    };

    return (
        <div className="min-h-screen bg-white flex overflow-hidden">
            <div className="hidden lg:flex lg:w-1/2 bg-primary p-16 flex-col justify-between relative overflow-hidden text-white">
                <div className="absolute top-0 right-0 -mr-24 -mt-24 w-96 h-96 bg-white/5 rounded-full"></div>
                <div className="absolute bottom-0 left-0 -ml-24 -mb-24 w-96 h-96 bg-white/5 rounded-full"></div>

                <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-12">
                        <div className="w-12 h-12 bg-white/10 rounded-2xl flex items-center justify-center border border-white/20">
                            <ShieldCheck size={28} />
                        </div>
                        <span className="text-2xl font-bold tracking-tight">CivicApp</span>
                    </div>

                    <div className="space-y-6 max-w-lg">
                        <h2 className="text-5xl font-bold leading-tight">
                            {t('signup.bannerTitle')}
                        </h2>
                        <p className="text-xl text-green-50 leading-relaxed font-medium">
                            {t('signup.bannerSubtitle')}
                        </p>
                    </div>
                </div>

                <div className="relative z-10 space-y-4 pt-8 border-t border-white/10">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center border border-white/20">
                            <ArrowRight size={18} />
                        </div>
                        <p className="text-sm font-bold tracking-wide">{t('signup.empowering')}</p>
                    </div>
                </div>
            </div>

            <div className="w-full lg:w-1/2 flex items-center justify-center p-8 lg:p-24 bg-white relative">
                <div className="absolute top-8 right-8">
                    <LanguageSelector />
                </div>

                <div className="w-full max-w-md space-y-10 animate-fade-in-up">
                    <div className="space-y-2 text-center lg:text-left">
                        <h1 className="text-4xl font-bold text-secondary tracking-tight">{t('signup.title')}</h1>
                        <p className="text-secondary/60 font-medium">{t('signup.signupHint')}</p>
                    </div>

                    {signupMode === 'standard' ? (
                        <form onSubmit={handleSignup} className="space-y-5">
                            <div className="space-y-2">
                                <label className="text-xs font-bold uppercase tracking-widest text-gray-400 ml-1">{t('signup.username')}</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-300 group-focus-within:text-primary transition-colors">
                                        <User size={18} />
                                    </div>
                                    <input
                                        type="text"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        placeholder="Choose a username"
                                        className="w-full h-14 pl-11 pr-4 bg-white border border-gray-100 rounded-2xl shadow-soft focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-secondary font-medium"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-bold uppercase tracking-widest text-gray-400 ml-1">{t('signup.email')}</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-300 group-focus-within:text-primary transition-colors">
                                        <Mail size={18} />
                                    </div>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="yourname@example.com"
                                        className="w-full h-14 pl-11 pr-4 bg-white border border-gray-100 rounded-2xl shadow-soft focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-secondary font-medium"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-bold uppercase tracking-widest text-gray-400 ml-1">{t('signup.password')}</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-300 group-focus-within:text-primary transition-colors">
                                        <Lock size={18} />
                                    </div>
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="••••••••"
                                        className="w-full h-14 pl-11 pr-4 bg-white border border-gray-100 rounded-2xl shadow-soft focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-secondary font-medium"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="pt-4">
                                <button type="submit" className="btn-primary w-full h-14 text-lg flex items-center justify-center gap-2 group shadow-lg">
                                    {t('signup.submit')}
                                    <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                                </button>
                            </div>
                        </form>
                    ) : (
                        <form onSubmit={handlePhoneSignup} className="space-y-5">
                            <div className="space-y-2">
                                <label className="text-xs font-bold uppercase tracking-widest text-gray-400 ml-1">{t('login.enterPhone')}</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-300 group-focus-within:text-primary transition-colors">
                                        <Phone size={18} />
                                    </div>
                                    <input
                                        type="tel"
                                        value={phoneNumber}
                                        onChange={(e) => setPhoneNumber(e.target.value)}
                                        placeholder="+91 00000 00000"
                                        className="w-full h-14 pl-11 pr-4 bg-white border border-gray-100 rounded-2xl shadow-soft focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-secondary font-medium"
                                        required
                                        disabled={isOtpSent}
                                    />
                                </div>
                            </div>

                            {isOtpSent && (
                                <div className="space-y-2 animate-fade-in-up">
                                    <label className="text-xs font-bold uppercase tracking-widest text-gray-400 ml-1">{t('login.enterOtp')}</label>
                                    <div className="relative group">
                                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-300 group-focus-within:text-primary transition-colors">
                                            <Lock size={18} />
                                        </div>
                                        <input
                                            type="text"
                                            value={otp}
                                            onChange={(e) => setOtp(e.target.value)}
                                            placeholder="0000"
                                            className="w-full h-14 pl-11 pr-4 bg-white border border-gray-100 rounded-2xl shadow-soft focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-secondary font-medium"
                                            maxLength={4}
                                            required
                                        />
                                    </div>
                                </div>
                            )}

                            <div className="pt-4">
                                <button type="submit" className="btn-primary w-full h-14 text-lg flex items-center justify-center gap-2 group shadow-lg">
                                    {isOtpSent ? t('login.verify') : t('login.sendCode')}
                                    <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                                </button>
                                {isOtpSent && (
                                    <button type="button" onClick={() => setIsOtpSent(false)} className="w-full mt-4 text-xs font-bold text-gray-400 uppercase tracking-widest hover:text-primary transition-colors">
                                        Change Number
                                    </button>
                                )}
                            </div>
                        </form>
                    )}

                    <div className="relative py-4">
                        <div className="absolute inset-0 flex items-center">
                            <span className="w-full border-t border-gray-100"></span>
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-white px-4 text-gray-400 font-bold tracking-widest">{t('signup.realTimeSignup')}</span>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <button type="button" onClick={() => handleSocialLogin('google')} className="flex items-center justify-center gap-3 h-14 border border-gray-100 rounded-2xl hover:bg-gray-50 transition-all shadow-soft group">
                                <svg className="w-5 h-5 group-hover:scale-110 transition-transform" viewBox="0 0 24 24">
                                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" />
                                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                                </svg>
                                <span className="text-sm font-bold text-secondary">Google</span>
                            </button>
                            <button type="button" onClick={() => handleSocialLogin('facebook')} className="flex items-center justify-center gap-3 h-14 border border-gray-100 rounded-2xl hover:bg-gray-50 transition-all shadow-soft group">
                                <Facebook size={20} className="text-[#1877F2] group-hover:scale-110 transition-transform" />
                                <span className="text-sm font-bold text-secondary">Facebook</span>
                            </button>
                        </div>

                        {signupMode === 'standard' ? (
                            <button type="button" onClick={() => setSignupMode('phone')} className="w-full flex items-center justify-center gap-3 h-14 border border-gray-100 rounded-2xl hover:bg-gray-50 transition-all shadow-soft group">
                                <Phone size={20} className="text-primary group-hover:scale-110 transition-transform" />
                                <span className="text-sm font-bold text-secondary">{t('signup.signupWithPhone')}</span>
                            </button>
                        ) : (
                            <button type="button" onClick={() => setSignupMode('standard')} className="w-full flex items-center justify-center gap-3 h-14 border border-gray-100 rounded-2xl hover:bg-gray-50 transition-all shadow-soft group">
                                <User size={20} className="text-primary group-hover:scale-110 transition-transform" />
                                <span className="text-sm font-bold text-secondary">Back to Standard Signup</span>
                            </button>
                        )}
                    </div>

                    <div className="text-center pt-2">
                        <p className="text-secondary/60 font-medium">
                            {t('signup.haveAccount')}{' '}
                            <Link to="/login" className="text-primary font-bold hover:underline">
                                {t('signup.loginLink')}
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Signup;
