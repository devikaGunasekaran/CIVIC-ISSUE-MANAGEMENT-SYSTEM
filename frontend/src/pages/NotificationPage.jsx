import { useEffect, useState } from 'react';
import api from '../api';
import { Bell } from 'lucide-react';

function NotificationPage() {
    const [notifications, setNotifications] = useState([]);

    useEffect(() => {
        // In a real app, this would fetch from a dedicated notifications endpoint
        // Here we simulate it by fetching recent complaints updates
        const fetchNotifications = async () => {
            try {
                const response = await api.get('/complaints/');
                // Mock notifications based on status
                const notifs = response.data.map(c => ({
                    id: c.id,
                    message: `Update: Complaint #${c.id} status is ${c.status}`,
                    time: c.updated_at,
                    category: c.category
                })).sort((a, b) => new Date(b.time) - new Date(a.time));

                setNotifications(notifs);
            } catch (error) {
                console.error('Error fetching notifications');
            }
        };
        fetchNotifications();
    }, []);

    return (
        <div className="home-container animate-fade-in">
            <h2 style={{ fontSize: '2rem', marginBottom: '20px', color: 'white', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Bell /> Notifications
            </h2>
            <div className="features-grid">
                {notifications.map((n) => (
                    <div key={n.id} className="glass-card" style={{ padding: '20px', textAlign: 'left', borderLeft: '4px solid #a855f7' }}>
                        <p style={{ color: '#cbd5e1', fontSize: '1.1rem' }}>{n.message}</p>
                        <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                            {new Date(n.time).toLocaleString()} • {n.category || 'General'}
                        </span>
                    </div>
                ))}
                {notifications.length === 0 && <p style={{ color: '#94a3b8' }}>No new notifications.</p>}
            </div>
        </div>
    );
}

export default NotificationPage;
