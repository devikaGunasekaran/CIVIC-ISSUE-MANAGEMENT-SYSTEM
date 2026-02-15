import { useEffect, useState } from 'react';
import api from '../api';
import { Loader2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

function Tracking() {
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchComplaints = async () => {
            try {
                const response = await api.get('/complaints/');
                setComplaints(response.data);
            } catch (error) {
                console.error('Error fetching complaints:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchComplaints();
    }, []);

    return (
        <div className="home-container animate-fade-in">
            <h2 style={{ fontSize: '2rem', marginBottom: '20px', color: 'white' }}>My Complaints</h2>

            {loading ? (
                <Loader2 className="animate-spin" size={48} color="#a855f7" />
            ) : (
                <div className="features-grid">
                    {complaints.length === 0 ? (
                        <p style={{ color: '#94a3b8' }}>No complaints found.</p>
                    ) : (
                        complaints.map((complaint) => (
                            <div key={complaint.id} className="feature-card glass-card" style={{ textAlign: 'left' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                    <span className={`status-badge status-${complaint.status}`}>
                                        {complaint.status}
                                    </span>
                                    <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                                        {new Date(complaint.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                                <h3 style={{ fontSize: '1.2rem', marginBottom: '10px', color: 'white' }}>
                                    {complaint.category || 'General Issue'}
                                </h3>
                                <p style={{ color: '#cbd5e1', marginBottom: '15px', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: '2', WebkitBoxOrient: 'vertical' }}>
                                    {complaint.description}
                                </p>
                                <Link to={`/complaint/${complaint.id}`} style={{ color: '#a855f7', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '5px' }}>
                                    View Details <ArrowRight size={16} />
                                </Link>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}

export default Tracking;
