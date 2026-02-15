import { useEffect, useState } from 'react';
import api from '../api';
import { Loader2, Filter, AlertCircle, CheckCircle, Clock, X, MapPin, Calendar, Search } from 'lucide-react';

function AdminDashboard() {
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filterStatus, setFilterStatus] = useState('ALL');
    const [filterPriority, setFilterPriority] = useState('ALL');
    const [selectedComplaint, setSelectedComplaint] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [notification, setNotification] = useState(null);

    const [adminArea, setAdminArea] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setAdminArea(payload.area);
            } catch (e) {
                console.error("Invalid token");
            }
        }
        fetchComplaints();
    }, []);

    const fetchComplaints = async () => {
        try {
            setLoading(true);
            const response = await api.get('/complaints/');
            setComplaints(response.data);
        } catch (error) {
            showNotification('Error fetching complaints', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleStatusUpdate = async (id, newStatus) => {
        try {
            await api.put(`/admin/complaints/${id}/status`, null, { params: { status: newStatus } });
            fetchComplaints();
            if (selectedComplaint && selectedComplaint.id === id) {
                setSelectedComplaint({ ...selectedComplaint, status: newStatus });
            }
            showNotification('Status updated successfully!', 'success');
        } catch (error) {
            showNotification('Failed to update status', 'error');
        }
    };

    const showNotification = (message, type) => {
        setNotification({ message, type });
        setTimeout(() => setNotification(null), 3000);
    };

    const filteredComplaints = complaints.filter(c => {
        const matchesStatus = filterStatus === 'ALL' || c.status === filterStatus;
        const matchesPriority = filterPriority === 'ALL' || c.priority === filterPriority;
        const matchesSearch = searchQuery === '' ||
            c.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
            c.location.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (c.category && c.category.toLowerCase().includes(searchQuery.toLowerCase()));
        return matchesStatus && matchesPriority && matchesSearch;
    });

    // Calculate stats
    const stats = {
        total: complaints.length,
        submitted: complaints.filter(c => c.status === 'SUBMITTED').length,
        inProgress: complaints.filter(c => c.status === 'IN_PROGRESS').length,
        resolved: complaints.filter(c => c.status === 'RESOLVED').length
    };

    return (
        <div className="home-container animate-fade-in" style={{ maxWidth: '1400px', padding: '40px 20px', position: 'relative' }}>
            {/* Notification Toast */}
            {notification && (
                <div style={{
                    position: 'fixed',
                    top: '100px',
                    right: '30px',
                    background: notification.type === 'success' ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                    color: 'white',
                    padding: '15px 25px',
                    borderRadius: '12px',
                    boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
                    zIndex: 2000,
                    animation: 'slideIn 0.3s ease-out',
                    fontWeight: '500'
                }}>
                    {notification.message}
                </div>
            )}

            {/* Header */}
            <div style={{ marginBottom: '40px' }}>
                <h2 style={{ fontSize: '2.5rem', color: 'white', marginBottom: '10px', fontWeight: '700' }}>
                    {adminArea ? `${adminArea} Zone Dashboard` : 'Chennai Corp Admin Dashboard'}
                </h2>
                <p style={{ color: '#94a3b8', fontSize: '1.1rem' }}>
                    Manage and track all civic complaints
                </p>
            </div>

            {/* Stats Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '40px' }}>
                <StatCard icon={<AlertCircle size={24} />} label="Total Complaints" value={stats.total} color="#6366f1" />
                <StatCard icon={<Clock size={24} />} label="Submitted" value={stats.submitted} color="#3b82f6" />
                <StatCard icon={<Loader2 size={24} />} label="In Progress" value={stats.inProgress} color="#eab308" />
                <StatCard icon={<CheckCircle size={24} />} label="Resolved" value={stats.resolved} color="#22c55e" />
            </div>

            {/* Search and Filters */}
            <div style={{
                background: 'rgba(30, 41, 59, 0.5)',
                padding: '25px',
                borderRadius: '16px',
                marginBottom: '30px',
                border: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
                <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', alignItems: 'center' }}>
                    {/* Search Bar */}
                    <div style={{ flex: '1', minWidth: '250px', position: 'relative' }}>
                        <Search size={20} color="#94a3b8" style={{ position: 'absolute', left: '15px', top: '50%', transform: 'translateY(-50%)' }} />
                        <input
                            type="text"
                            placeholder="Search complaints..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '12px 15px 12px 45px',
                                background: '#1e293b',
                                border: '1px solid #334155',
                                borderRadius: '10px',
                                color: 'white',
                                fontSize: '0.95rem',
                                outline: 'none'
                            }}
                        />
                    </div>

                    {/* Status Filter */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Filter size={18} color="#94a3b8" />
                        <select
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            style={{
                                background: '#1e293b',
                                border: '1px solid #334155',
                                color: 'white',
                                padding: '12px 15px',
                                borderRadius: '10px',
                                fontSize: '0.95rem',
                                cursor: 'pointer',
                                minWidth: '150px'
                            }}
                        >
                            <option value="ALL">All Status</option>
                            <option value="SUBMITTED">Submitted</option>
                            <option value="IN_PROGRESS">In Progress</option>
                            <option value="RESOLVED">Resolved</option>
                        </select>
                    </div>

                    {/* Priority Filter */}
                    <select
                        value={filterPriority}
                        onChange={(e) => setFilterPriority(e.target.value)}
                        style={{
                            background: '#1e293b',
                            border: '1px solid #334155',
                            color: 'white',
                            padding: '12px 15px',
                            borderRadius: '10px',
                            fontSize: '0.95rem',
                            cursor: 'pointer',
                            minWidth: '150px'
                        }}
                    >
                        <option value="ALL">All Priorities</option>
                        <option value="LOW">Low</option>
                        <option value="MEDIUM">Medium</option>
                        <option value="HIGH">High</option>
                        <option value="CRITICAL">Critical</option>
                    </select>

                    {/* Results Count */}
                    <div style={{
                        color: '#94a3b8',
                        fontSize: '0.9rem',
                        padding: '0 10px'
                    }}>
                        {filteredComplaints.length} {filteredComplaints.length === 1 ? 'complaint' : 'complaints'}
                    </div>
                </div>
            </div>

            {/* Complaints Grid */}
            {loading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '80px' }}>
                    <Loader2 className="animate-spin" size={48} color="#a855f7" />
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '24px' }}>
                    {filteredComplaints.length === 0 ? (
                        <div style={{
                            gridColumn: '1 / -1',
                            textAlign: 'center',
                            padding: '60px 20px',
                            background: 'rgba(30, 41, 59, 0.3)',
                            borderRadius: '16px',
                            border: '2px dashed rgba(255, 255, 255, 0.1)'
                        }}>
                            <AlertCircle size={48} color="#64748b" style={{ marginBottom: '15px' }} />
                            <p style={{ color: '#94a3b8', fontSize: '1.1rem', marginBottom: '5px' }}>No complaints found</p>
                            <p style={{ color: '#64748b', fontSize: '0.9rem' }}>Try adjusting your filters or search query</p>
                        </div>
                    ) : (
                        filteredComplaints.map((complaint, index) => (
                            <ComplaintCard
                                key={complaint.id}
                                complaint={complaint}
                                onClick={() => setSelectedComplaint(complaint)}
                                index={index}
                            />
                        ))
                    )}
                </div>
            )}

            {/* Modal for Complaint Details */}
            {selectedComplaint && (
                <ComplaintModal
                    complaint={selectedComplaint}
                    onClose={() => setSelectedComplaint(null)}
                    onStatusUpdate={handleStatusUpdate}
                />
            )}
        </div>
    );
}

function StatCard({ icon, label, value, color }) {
    return (
        <div className="glass-card" style={{ padding: '25px', display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ color: color, background: `${color}20`, padding: '15px', borderRadius: '12px' }}>
                {icon}
            </div>
            <div>
                <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '5px' }}>{label}</p>
                <h3 style={{ color: 'white', fontSize: '2rem', margin: 0 }}>{value}</h3>
            </div>
        </div>
    );
}

function ComplaintCard({ complaint, onClick, index }) {
    const getPriorityColor = (priority) => {
        switch (priority) {
            case 'CRITICAL': return '#ef4444';
            case 'HIGH': return '#f97316';
            case 'MEDIUM': return '#eab308';
            case 'LOW': return '#22c55e';
            default: return '#94a3b8';
        }
    };

    return (
        <div
            className="glass-card"
            onClick={onClick}
            style={{
                padding: '25px',
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                animation: `fadeInUp 0.5s ease-out ${index * 0.1}s both`,
                ':hover': { transform: 'translateY(-5px)' }
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
        >
            {/* Add keyframes for animation */}
            <style>{`
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>

            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '15px' }}>
                <div>
                    <p style={{ color: '#a855f7', fontSize: '0.85rem', fontWeight: '600', marginBottom: '5px' }}>
                        {complaint.category || 'General'}
                    </p>
                    <p style={{ color: 'white', fontWeight: 'bold', fontSize: '1.1rem' }}>#{complaint.id}</p>
                </div>
                <span className={`status-badge status-${complaint.status}`} style={{ fontSize: '0.75rem' }}>
                    {complaint.status.replace('_', ' ')}
                </span>
            </div>

            {/* Description */}
            <p style={{
                color: '#cbd5e1',
                fontSize: '0.95rem',
                lineHeight: '1.5',
                marginBottom: '15px',
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
            }}>
                {complaint.description}
            </p>

            {/* Location */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}>
                <MapPin size={16} color="#64748b" />
                <p style={{ color: '#64748b', fontSize: '0.85rem' }}>{complaint.location}</p>
            </div>
            {/* Area */}
            {complaint.area && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}>
                    <MapPin size={16} color="#a855f7" />
                    <p style={{ color: '#a855f7', fontSize: '0.85rem' }}>Area: {complaint.area}</p>
                </div>
            )}

            {/* Priority Badge */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{
                    color: getPriorityColor(complaint.priority),
                    background: `${getPriorityColor(complaint.priority)}20`,
                    padding: '6px 12px',
                    borderRadius: '6px',
                    fontSize: '0.8rem',
                    fontWeight: '600'
                }}>
                    {complaint.priority}
                </span>
                <p style={{ color: '#64748b', fontSize: '0.8rem' }}>
                    {new Date(complaint.created_at).toLocaleDateString()}
                </p>
            </div>
        </div>
    );
}

function ComplaintModal({ complaint, onClose, onStatusUpdate }) {
    const getPriorityColor = (priority) => {
        switch (priority) {
            case 'CRITICAL': return '#ef4444';
            case 'HIGH': return '#f97316';
            case 'MEDIUM': return '#eab308';
            case 'LOW': return '#22c55e';
            default: return '#94a3b8';
        }
    };

    return (
        <div
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(0, 0, 0, 0.8)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                padding: '20px'
            }}
            onClick={onClose}
        >
            <div
                className="glass-card"
                onClick={(e) => e.stopPropagation()}
                style={{
                    maxWidth: '600px',
                    width: '100%',
                    maxHeight: '90vh',
                    overflow: 'auto',
                    padding: '30px',
                    position: 'relative'
                }}
            >
                {/* Close Button */}
                <button
                    onClick={onClose}
                    style={{
                        position: 'absolute',
                        top: '20px',
                        right: '20px',
                        background: 'rgba(255, 255, 255, 0.1)',
                        border: 'none',
                        borderRadius: '50%',
                        width: '35px',
                        height: '35px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        color: 'white'
                    }}
                >
                    <X size={20} />
                </button>

                {/* Header */}
                <div style={{ marginBottom: '25px' }}>
                    <p style={{ color: '#a855f7', fontSize: '0.9rem', fontWeight: '600', marginBottom: '8px' }}>
                        {complaint.category || 'General'}
                    </p>
                    <h2 style={{ color: 'white', fontSize: '1.8rem', marginBottom: '10px' }}>
                        Complaint #{complaint.id}
                    </h2>
                    <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                        <span className={`status-badge status-${complaint.status}`}>
                            {complaint.status.replace('_', ' ')}
                        </span>
                        <span style={{
                            color: getPriorityColor(complaint.priority),
                            background: `${getPriorityColor(complaint.priority)}20`,
                            padding: '6px 12px',
                            borderRadius: '6px',
                            fontSize: '0.85rem',
                            fontWeight: '600'
                        }}>
                            {complaint.priority} Priority
                        </span>
                    </div>
                </div>

                {/* Description */}
                <div style={{ marginBottom: '25px' }}>
                    <h3 style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        Description
                    </h3>
                    <p style={{ color: '#cbd5e1', fontSize: '1rem', lineHeight: '1.6' }}>
                        {complaint.description}
                    </p>
                </div>

                {/* Location */}
                <div style={{ marginBottom: '25px' }}>
                    <h3 style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        Location
                    </h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <MapPin size={18} color="#6366f1" />
                        <p style={{ color: '#cbd5e1', fontSize: '1rem' }}>{complaint.location}</p>
                    </div>
                </div>

                {/* Area */}
                <div style={{ marginBottom: '25px' }}>
                    <h3 style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        Area
                    </h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <MapPin size={18} color="#a855f7" />
                        <p style={{ color: '#cbd5e1', fontSize: '1rem' }}>{complaint.area || 'N/A'}</p>
                    </div>
                </div>

                {/* Date */}
                <div style={{ marginBottom: '25px' }}>
                    <h3 style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        Submitted On
                    </h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Calendar size={18} color="#6366f1" />
                        <p style={{ color: '#cbd5e1', fontSize: '1rem' }}>
                            {new Date(complaint.created_at).toLocaleString()}
                        </p>
                    </div>
                </div>

                {/* Update Status */}
                <div>
                    <h3 style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                        Update Status
                    </h3>
                    <select
                        value={complaint.status}
                        onChange={(e) => onStatusUpdate(complaint.id, e.target.value)}
                        style={{
                            width: '100%',
                            padding: '12px 15px',
                            background: '#1e293b',
                            border: '1px solid #334155',
                            color: 'white',
                            borderRadius: '8px',
                            fontSize: '1rem',
                            cursor: 'pointer'
                        }}
                    >
                        <option value="SUBMITTED">Submitted</option>
                        <option value="IN_PROGRESS">In Progress</option>
                        <option value="RESOLVED">Resolved</option>
                    </select>
                </div>
            </div>
        </div>
    );
}

export default AdminDashboard;
