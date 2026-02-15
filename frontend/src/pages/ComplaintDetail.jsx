import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import api from '../api';
import { Loader2, ArrowLeft, CheckCircle } from 'lucide-react';

function ComplaintDetail() {
    const { id } = useParams();
    const [complaint, setComplaint] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const location = useLocation();
    const isSuccess = location.state?.success;

    useEffect(() => {
        const fetchComplaint = async () => {
            try {
                const response = await api.get(`/complaints/${id}`);
                setComplaint(response.data);
            } catch (error) {
                alert('Error fetching complaint details: ' + (error.response?.data?.detail || error.message));
                navigate('/track');
            } finally {
                setLoading(false);
            }
        };
        fetchComplaint();
    }, [id, navigate]);

    if (loading) return <div className="home-container"><Loader2 className="animate-spin" size={48} /></div>;
    if (!complaint) return <div className="home-container">Complaint not found</div>;

    return (
        <div className="home-container animate-fade-in">
            {isSuccess && (
                <div className="glass-card" style={{ maxWidth: '800px', width: '100%', marginBottom: '20px', padding: '20px', borderLeft: '4px solid #22c55e', background: 'rgba(34, 197, 94, 0.1)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <CheckCircle color="#22c55e" />
                        <span style={{ color: '#22c55e', fontSize: '1.2rem', fontWeight: 'bold' }}>Complaint Submitted Successfully!</span>
                    </div>
                    <p style={{ marginTop: '10px', color: '#cbd5e1' }}>
                        Reference ID: <strong>{complaint.id}</strong><br />
                        Estimated Resolution: <strong>24-48 Hours</strong>
                    </p>
                </div>
            )}

            <div className="glass-card" style={{ maxWidth: '800px', width: '100%', textAlign: 'left' }}>
                <button onClick={() => navigate(-1)} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <ArrowLeft size={20} /> Back
                </button>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h2 style={{ fontSize: '2rem', color: 'white' }}>Complaint #{complaint.id}</h2>
                    <span className={`status-badge status-${complaint.status}`}>{complaint.status}</span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
                    <div>
                        <h4 style={{ color: '#94a3b8', marginBottom: '5px' }}>Category</h4>
                        <p style={{ color: 'white', marginBottom: '20px' }}>{complaint.category || 'N/A'}</p>

                        <h4 style={{ color: '#94a3b8', marginBottom: '5px' }}>Description</h4>
                        <p style={{ color: '#cbd5e1', marginBottom: '20px', lineHeight: '1.6' }}>{complaint.description}</p>

                        <h4 style={{ color: '#94a3b8', marginBottom: '5px' }}>Location</h4>
                        <p style={{ color: '#cbd5e1', marginBottom: '20px' }}>{complaint.location}</p>

                        <h4 style={{ color: '#94a3b8', marginBottom: '5px' }}>Priority</h4>
                        <p style={{ color: getPriorityColor(complaint.priority), fontWeight: 'bold' }}>{complaint.priority}</p>
                    </div>

                    <div>
                        {complaint.image_url && (
                            <img
                                src={`http://localhost:8000/uploads/${complaint.image_url.split('/').pop()}`}
                                alt="Evidence"
                                style={{ width: '100%', borderRadius: '12px', border: '1px solid #334155' }}
                            />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function getPriorityColor(priority) {
    switch (priority) {
        case 'CRITICAL': return '#ef4444';
        case 'HIGH': return '#f97316';
        case 'MEDIUM': return '#eab308';
        case 'LOW': return '#22c55e';
        default: return '#94a3b8';
    }
}

export default ComplaintDetail;
