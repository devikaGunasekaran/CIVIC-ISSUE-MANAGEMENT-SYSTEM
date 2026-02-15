import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { MapPin, Camera, Mic, Loader2, StopCircle, Trash2, Volume2, Upload, Info, FileAudio } from 'lucide-react';

function ReportIssue() {
    const [description, setDescription] = useState('');
    const [location, setLocation] = useState('');
    const [area, setArea] = useState('Ambattur'); // Default
    const [image, setImage] = useState(null);
    const [audioFile, setAudioFile] = useState(null);
    const [loading, setLoading] = useState(false);

    // Voice Recording States
    const [isRecording, setIsRecording] = useState(false);
    const [audioURL, setAudioURL] = useState(null);
    const mediaRecorder = useRef(null);
    const audioChunks = useRef([]);

    const navigate = useNavigate();

    const handleLocation = () => {
        if (navigator.geolocation) {
            setLoading(true);
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    setLocation(`${position.coords.latitude}, ${position.coords.longitude}`);
                    setLoading(false);
                },
                (error) => {
                    alert('Error getting location: ' + error.message);
                    setLoading(false);
                }
            );
        } else {
            alert('Geolocation is not supported by this browser.');
        }
    };

    // --- AUDIO RECORDING ---
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder.current = new MediaRecorder(stream);
            audioChunks.current = [];

            mediaRecorder.current.ondataavailable = (event) => {
                audioChunks.current.push(event.data);
            };

            mediaRecorder.current.onstop = () => {
                const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
                const url = URL.createObjectURL(audioBlob);
                setAudioURL(url);
                const file = new File([audioBlob], `voice_${Date.now()}.wav`, { type: 'audio/wav' });
                setAudioFile(file);
            };

            mediaRecorder.current.start();
            setIsRecording(true);
        } catch (err) {
            alert('Mic Error: ' + err.message);
        }
    };

    const stopRecording = () => {
        if (mediaRecorder.current && isRecording) {
            mediaRecorder.current.stop();
            setIsRecording(false);
            mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
        }
    };

    // --- AUDIO UPLOAD ---
    const handleAudioUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (!file.type.startsWith('audio/')) {
                alert('Please upload a valid audio file.');
                return;
            }
            setAudioFile(file);
            setAudioURL(URL.createObjectURL(file));
        }
    };

    const deleteAudio = () => {
        setAudioURL(null);
        setAudioFile(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!description && !audioFile) {
            alert('🚨 Please provide either a Text Description or a Voice Message/File.');
            return;
        }

        if (!location) {
            alert('📍 Please fetch your GPS location first!');
            return;
        }

        try {
            setLoading(true);
            const formData = new FormData();
            formData.append('description', description || "");
            formData.append('location', location);
            formData.append('area', area);

            if (image) formData.append('image', image);
            if (audioFile) formData.append('audio', audioFile);

            const response = await api.post('/complaints/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            navigate(`/complaint/${response.data.id}`, { state: { success: true } });
        } catch (error) {
            alert('Error: ' + (error.response?.data?.detail || error.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-container glass-card animate-fade-in" style={{ maxWidth: '650px', margin: '2rem auto' }}>
            <h2 className="form-title" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📢 Report Issue</h2>
            <p style={{ color: '#94a3b8', marginBottom: '25px', fontSize: '0.95rem' }}>
                Fill in the details below. Our AI Agents will automatically prioritize and route your complaint.
            </p>

            <form onSubmit={handleSubmit}>

                {/* 1. AUDIO SECTION (RECORD OR UPLOAD) */}
                <div className="form-group" style={{
                    background: '#0f172a',
                    padding: '25px',
                    borderRadius: '16px',
                    border: '1px solid #1e293b',
                    boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.3)'
                }}>
                    <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px', fontWeight: '700' }}>
                        <Mic size={20} color="#10b981" /> Voice Description
                    </label>

                    {!audioURL ? (
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
                            {!isRecording ? (
                                <div style={{ display: 'flex', gap: '15px', width: '100%', justifyContent: 'center' }}>
                                    {/* Record Button */}
                                    <button
                                        type="button"
                                        onClick={startRecording}
                                        style={{
                                            background: 'var(--primary-gradient)',
                                            flex: 1, height: '60px', borderRadius: '12px',
                                            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
                                            border: 'none', cursor: 'pointer', fontWeight: 'bold'
                                        }}
                                    >
                                        <Mic size={24} /> Record Voice
                                    </button>

                                    {/* Upload Button */}
                                    <label style={{
                                        background: '#1e293b', flex: 1, height: '60px', borderRadius: '12px',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
                                        border: '1px solid #334155', cursor: 'pointer', fontWeight: 'bold',
                                        color: '#94a3b8'
                                    }}>
                                        <Upload size={24} /> Upload File
                                        <input type="file" hidden accept="audio/*" onChange={handleAudioUpload} />
                                    </label>
                                </div>
                            ) : (
                                <button
                                    type="button"
                                    onClick={stopRecording}
                                    className="pulsing"
                                    style={{
                                        background: '#ef4444', width: '80px', height: '80px',
                                        borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        border: 'none', cursor: 'pointer'
                                    }}
                                >
                                    <StopCircle size={32} />
                                </button>
                            )}
                            <span style={{ fontSize: '0.85rem', color: isRecording ? '#ef4444' : '#94a3b8', fontWeight: isRecording ? 'bold' : 'normal' }}>
                                {isRecording ? 'Recording active... click to stop' : 'Help illiterate users by recording a voice message in any language'}
                            </span>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: '#1e293b', padding: '12px', borderRadius: '12px' }}>
                                <FileAudio size={24} color="#10b981" />
                                <div style={{ flexGrow: 1, overflow: 'hidden' }}>
                                    <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '5px' }}>
                                        {audioFile?.name || 'Voice Message'}
                                    </div>
                                    <audio src={audioURL} controls style={{ width: '100%', height: '35px' }} />
                                </div>
                                <button
                                    type="button"
                                    onClick={deleteAudio}
                                    style={{ background: 'transparent', border: 'none', color: '#f87171', cursor: 'pointer', padding: '5px' }}
                                >
                                    <Trash2 size={22} />
                                </button>
                            </div>
                            <span style={{ fontSize: '0.75rem', color: '#10b981', textAlign: 'center' }}>
                                ✅ Audio attached successfully
                            </span>
                        </div>
                    )}
                </div>

                <div style={{ textAlign: 'center', margin: '15px 0', color: '#475569', fontSize: '0.8rem', fontWeight: 'bold' }}>OR</div>

                {/* 2. TEXT DESCRIPTION (OPTIONAL) */}
                <div className="form-group">
                    <label className="form-label">Written Details (Optional)</label>
                    <textarea
                        rows="3"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Add additional details if needed..."
                        style={{ background: '#0f172a', border: '1px solid #1e293b' }}
                    />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                    {/* 3. LOCATION */}
                    <div className="form-group">
                        <label className="form-label">GPS Location</label>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            <input
                                type="text"
                                value={location}
                                readOnly
                                placeholder="Detect GPS"
                                style={{ margin: 0, background: '#0f172a', fontSize: '0.85rem' }}
                            />
                            <button
                                type="button"
                                onClick={handleLocation}
                                className="secondary-action"
                                style={{ padding: '0 12px', height: '48px' }}
                            >
                                {loading ? <Loader2 className="animate-spin" /> : <MapPin size={20} />}
                            </button>
                        </div>
                    </div>

                    {/* 4. AREA SELECTION */}
                    <div className="form-group">
                        <label className="form-label">Select Zone</label>
                        <select
                            value={area}
                            onChange={(e) => setArea(e.target.value)}
                            style={{ margin: 0, background: '#0f172a', border: '1px solid #1e293b' }}
                        >
                            <option value="Ambattur">Ambattur</option>
                            <option value="Avadi">Avadi</option>
                            <option value="Perambur">Perambur</option>
                            <option value="Anna Nagar">Anna Nagar</option>
                            <option value="Adyar">Adyar</option>
                            <option value="Velachery">Velachery</option>
                        </select>
                    </div>
                </div>

                {/* 5. IMAGE UPLOAD */}
                <div className="form-group" style={{ marginTop: '10px' }}>
                    <label className="form-label">Evidence Photo</label>
                    <div style={{
                        border: '2px dashed #1e293b',
                        borderRadius: '16px',
                        padding: '20px',
                        textAlign: 'center',
                        cursor: 'pointer',
                        background: '#0f172a'
                    }}>
                        <input
                            type="file"
                            id="file-upload"
                            hidden
                            accept="image/*"
                            onChange={(e) => setImage(e.target.files[0])}
                        />
                        <label htmlFor="file-upload" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                            <Camera size={32} color="#10b981" />
                            <span style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
                                {image ? `✅ ${image.name}` : 'Click to add a photo'}
                            </span>
                        </label>
                    </div>
                </div>

                <div style={{
                    display: 'flex', alignItems: 'flex-start', gap: '10px',
                    background: 'rgba(16, 185, 129, 0.05)', padding: '15px',
                    borderRadius: '12px', marginBottom: '20px', border: '1px solid rgba(16, 185, 129, 0.1)'
                }}>
                    <Info size={18} color="#10b981" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: '1.4' }}>
                        Our AI analyzes your voice/text to detect <strong>critical infrastructure</strong> (Schools/Hospitals) and assigns priority levels automatically.
                    </p>
                </div>

                <button
                    type="submit"
                    className="submit-btn"
                    disabled={loading}
                    style={{
                        width: '100%', padding: '18px', fontSize: '1.2rem',
                        fontWeight: '800', display: 'flex', justifyContent: 'center',
                        alignItems: 'center', gap: '12px', borderRadius: '16px'
                    }}
                >
                    {loading ? <Loader2 className="animate-spin" /> : '🚀 Submit Complaint'}
                </button>
            </form>
        </div>
    );
}

export default ReportIssue;
