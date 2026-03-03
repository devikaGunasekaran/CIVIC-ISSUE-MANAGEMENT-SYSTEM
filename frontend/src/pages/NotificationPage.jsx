import { useEffect, useState } from 'react';
import api from '../api';
import { Bell, Info, CheckCircle2, AlertCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';

function NotificationPage() {
    const [notifications, setNotifications] = useState([]);
    const { t } = useTranslation();

    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                const response = await api.get('/complaints/');
                const notifs = response.data.map(c => ({
                    id: c.id,
                    message: `Update: Complaint #${c.id} status is ${c.status}`,
                    time: c.updated_at,
                    category: c.category,
                    status: c.status
                })).sort((a, b) => new Date(b.time) - new Date(a.time));

                setNotifications(notifs);
            } catch (error) {
                console.error('Error fetching notifications');
            }
        };
        fetchNotifications();
    }, []);

    const getStatusIcon = (status) => {
        switch (status) {
            case 'RESOLVED': return <CheckCircle2 className="text-primary" size={20} />;
            case 'SUBMITTED': return <Info className="text-blue-500" size={20} />;
            default: return <Bell className="text-amber-500" size={20} />;
        }
    };

    return (
        <div className="max-w-4xl mx-auto py-12 px-8 space-y-10 animate-fade-in-up bg-white min-h-screen">
            <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gray-50 rounded-2xl flex items-center justify-center text-primary shadow-sm border border-gray-100">
                    <Bell size={24} />
                </div>
                <div className="space-y-1">
                    <h2 className="text-3xl font-extrabold text-secondary tracking-tight">
                        {t('notifications.title')}
                    </h2>
                    <p className="text-secondary/60 text-sm font-medium">Real-time alerts from your city infrastructure</p>
                </div>
            </div>

            <div className="space-y-4">
                {notifications.map((n) => (
                    <div key={n.id} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-soft hover:shadow-premium transition-all flex items-start gap-5">
                        <div className="mt-1">
                            {getStatusIcon(n.status)}
                        </div>
                        <div className="flex-1 space-y-2">
                            <p className="text-secondary font-semibold leading-relaxed">{n.message}</p>
                            <div className="flex items-center gap-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                                <span>{new Date(n.time).toLocaleString()}</span>
                                <span className="w-1 h-1 bg-gray-200 rounded-full"></span>
                                <span className="text-primary/70">{n.category || 'General'}</span>
                            </div>
                        </div>
                    </div>
                ))}
                {notifications.length === 0 && (
                    <div className="py-20 text-center space-y-4 bg-gray-50 rounded-3xl border-2 border-dashed border-gray-100">
                        <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center text-gray-200 mx-auto shadow-sm">
                            <Bell size={32} />
                        </div>
                        <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">{t('notifications.noNotifications')}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default NotificationPage;
