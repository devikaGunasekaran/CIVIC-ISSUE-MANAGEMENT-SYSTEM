import { useState, useEffect } from 'react';
import api from '../api';
import { User, Phone, Mail, Save, CheckCircle2, AlertCircle, Shield, Bell } from 'lucide-react';
import { useTranslation } from 'react-i18next';

function Profile() {
    const [profile, setProfile] = useState(null);
    const [phone, setPhone] = useState('');
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [successMsg, setSuccessMsg] = useState('');
    const [errorMsg, setErrorMsg] = useState('');
    const { t } = useTranslation();

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get('/users/me');
                setProfile(res.data);
                setPhone(res.data.phone || '');
                setEmail(res.data.email || '');
            } catch (err) {
                console.error('Failed to load profile', err);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, []);

    const handleSave = async (e) => {
        e.preventDefault();
        setSaving(true);
        setSuccessMsg('');
        setErrorMsg('');
        try {
            const res = await api.put('/users/me', { phone: phone || null, email });
            setProfile(res.data);
            setSuccessMsg('Profile updated successfully! You will now receive SMS alerts.');
        } catch (err) {
            setErrorMsg(err.response?.data?.detail || 'Failed to update profile.');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
        </div>
    );

    return (
        <div className="max-w-2xl mx-auto py-12 px-6 animate-fade-in-up">
            {/* Header */}
            <div className="mb-10 space-y-2">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-primary rounded-2xl flex items-center justify-center text-white shadow-lg">
                        <User size={26} />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-secondary tracking-tight">My Profile</h1>
                        <p className="text-earth/50 font-medium text-sm">Manage your account details and notification preferences</p>
                    </div>
                </div>
            </div>

            {/* Account Info Card */}
            <div className="bg-white rounded-3xl border border-gray-100 shadow-soft p-8 mb-6 space-y-4">
                <div className="flex items-center gap-3 pb-4 border-b border-gray-50">
                    <Shield size={18} className="text-primary" />
                    <h2 className="text-sm font-bold text-secondary uppercase tracking-widest">Account Info</h2>
                </div>
                <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center text-primary font-bold text-2xl">
                        {profile?.username?.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <p className="text-xl font-bold text-secondary">{profile?.username}</p>
                        <p className="text-sm text-earth/50 font-mono capitalize">{profile?.role}</p>
                    </div>
                </div>
            </div>

            {/* Notification Preferences Form */}
            <div className="bg-white rounded-3xl border border-gray-100 shadow-soft p-8 space-y-6">
                <div className="flex items-center gap-3 pb-4 border-b border-gray-50">
                    <Bell size={18} className="text-primary" />
                    <h2 className="text-sm font-bold text-secondary uppercase tracking-widest">Notification Details</h2>
                </div>

                {successMsg && (
                    <div className="bg-green-50 border border-green-100 text-green-700 px-4 py-3 rounded-2xl flex items-center gap-3 animate-fade-in-up">
                        <CheckCircle2 size={18} />
                        <span className="text-sm font-bold">{successMsg}</span>
                    </div>
                )}
                {errorMsg && (
                    <div className="bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-2xl flex items-center gap-3 animate-fade-in-up">
                        <AlertCircle size={18} />
                        <span className="text-sm font-bold">{errorMsg}</span>
                    </div>
                )}

                <form onSubmit={handleSave} className="space-y-5">
                    {/* Email Field */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold uppercase tracking-widest text-gray-400">Email Address</label>
                        <div className="relative group">
                            <Mail size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-300 group-focus-within:text-primary transition-colors" />
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full h-14 pl-11 pr-4 bg-white border border-gray-100 rounded-2xl shadow-soft focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-secondary font-medium"
                                required
                            />
                        </div>
                    </div>

                    {/* Phone Field */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold uppercase tracking-widest text-gray-400">
                            Phone Number
                            <span className="ml-2 text-gray-300 font-normal normal-case tracking-normal">(receives SMS status alerts)</span>
                        </label>
                        <div className="relative group">
                            <Phone size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-300 group-focus-within:text-primary transition-colors" />
                            <input
                                type="tel"
                                value={phone}
                                onChange={(e) => setPhone(e.target.value)}
                                placeholder="+91 98765 43210 (with country code)"
                                className="w-full h-14 pl-11 pr-4 bg-white border border-gray-100 rounded-2xl shadow-soft focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-secondary font-medium"
                            />
                        </div>
                        <p className="text-[10px] text-gray-400 mt-1 ml-1 italic">Note: Use + prefix for numbers outside India (e.g. +1...)</p>
                        {!phone && (
                            <p className="text-xs text-amber-500 font-bold flex items-center gap-1.5 ml-1">
                                <AlertCircle size={12} />
                                No phone number on file — SMS notifications are disabled
                            </p>
                        )}
                        {phone && (
                            <p className="text-xs text-primary font-bold flex items-center gap-1.5 ml-1">
                                <CheckCircle2 size={12} />
                                SMS notifications are active for this number
                            </p>
                        )}
                    </div>

                    <div className="pt-2">
                        <button
                            type="submit"
                            disabled={saving}
                            className="w-full h-14 bg-primary text-white font-bold rounded-2xl shadow-lg shadow-green-100 hover:bg-primary/90 transition-all flex items-center justify-center gap-2 disabled:opacity-70"
                        >
                            {saving ? (
                                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                            ) : (
                                <>
                                    <Save size={18} />
                                    Save Changes
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Profile;
