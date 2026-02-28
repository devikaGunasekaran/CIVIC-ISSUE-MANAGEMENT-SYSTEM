import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import api from '../api';
import {
    extractLocationFromText,
    mapAreaToZone,
    transcribeWithSpeechAPI,
    runOCRPipeline,
    fuzzyMatchCategory,
    detectZoneFromAddress,
    detectZoneFromAreaName,
    forwardGeocode,
    GCC_ZONE_MAP,
} from '../utils/locationExtractor';
import {
    MapPin, Camera, Mic, Loader2, StopCircle, Trash2,
    Upload, Info, FileAudio, FileImage,
    ChevronRight, ChevronLeft, CheckCircle2, ShieldAlert,
    Sparkles, Send, PenTool, Navigation, Edit3, AlertTriangle, Volume2, ScanText, LocateFixed
} from 'lucide-react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default marker icons (broken in Vite/Webpack builds)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const CHENNAI_CENTER = [13.0827, 80.2707]; // Chennai default center

// ─── Map Click Handler (inner component) ──────────────────────────────────────
function MapClickHandler({ onPick }) {
    useMapEvents({
        click(e) {
            onPick(e.latlng.lat, e.latlng.lng);
        },
    });
    return null;
}

// ─── Detection Banner ──────────────────────────────────────────────────────────
function DetectionBanner({ detected, source, onAccept, onDismiss }) {
    if (!detected || !detected.areaName) return null;
    const sourceLabel = source === 'voice' ? '🎤 From Voice' : source === 'image' ? '🖼️ From Image' : '📝 From Text';
    return (
        <div className="bg-green-50 border border-green-200 rounded-2xl p-4 flex items-start gap-3 animate-fade-in-up">
            <div className="w-9 h-9 bg-green-100 rounded-xl flex items-center justify-center shrink-0">
                <Sparkles size={16} className="text-green-600" />
            </div>
            <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-green-800">
                    {sourceLabel} — Area: <span className="text-green-600">{detected.areaName}</span>
                    {detected.landmark && <span className="text-green-600/70"> · Landmark: {detected.landmark}</span>}
                </p>
                <p className="text-xs text-green-600/60 mt-0.5">Location auto-detected. Accept to auto-fill fields.</p>
            </div>
            <div className="flex gap-2 shrink-0">
                <button type="button" onClick={onAccept}
                    className="px-3 py-1.5 bg-green-600 text-white text-xs font-bold rounded-xl hover:bg-green-700 transition-colors">
                    Accept
                </button>
                <button type="button" onClick={onDismiss}
                    className="px-3 py-1.5 bg-white text-green-700 text-xs font-bold rounded-xl border border-green-200 hover:bg-green-50 transition-colors">
                    Dismiss
                </button>
            </div>
        </div>
    );
}

// ─── Main Component ────────────────────────────────────────────────────────────
function ReportIssue() {
    const [step, setStep] = useState(1);
    const [description, setDescription] = useState('');
    const [location, setLocation] = useState('');
    const [area, setArea] = useState('');               // GCC Zone for submission
    const [autoZone, setAutoZone] = useState(null);     // auto-detected GCC zone
    const [zoneLoading, setZoneLoading] = useState(false);  // zone detection in progress
    const [image, setImage] = useState(null);
    const [audioFile, setAudioFile] = useState(null);
    const [paperComplaint, setPaperComplaint] = useState(null);
    const [loading, setLoading] = useState(false);
    const [locationError, setLocationError] = useState('');

    // ── Map State ───────────────────────────────────────────────────────────
    const [mapPin, setMapPin] = useState(null);           // { lat, lng }
    const [mapAddress, setMapAddress] = useState('');     // Reverse geocoded address
    const [mapLoading, setMapLoading] = useState(false);
    useEffect(() => {
        console.log('--- VOICE_PIPELINE_V3.2_ACTIVE ---');
    }, []);

    const [locationMode, setLocationMode] = useState('map'); // 'map' | 'manual'
    const mapRef = useRef(null);

    // ── Manual Fields ───────────────────────────────────────────────────────
    const [manualArea, setManualArea] = useState('');
    const [manualLandmark, setManualLandmark] = useState('');
    const [manualPincode, setManualPincode] = useState('');

    // ── Detection State ─────────────────────────────────────────────────────
    const [detectedLocation, setDetectedLocation] = useState(null);
    const [detectedSource, setDetectedSource] = useState(null);
    const [detectedAccepted, setDetectedAccepted] = useState(false);

    // ── Conflict ────────────────────────────────────────────────────────────
    const [showConflictDialog, setShowConflictDialog] = useState(false);
    const [mapAreaName, setMapAreaName] = useState('');

    // ── Voice State ─────────────────────────────────────────────────────────
    const [isRecording, setIsRecording] = useState(false);
    const [audioURL, setAudioURL] = useState(null);
    const [voiceTranscript, setVoiceTranscript] = useState('');
    const [voiceDetecting, setVoiceDetecting] = useState(false);
    const [voiceConfidence, setVoiceConfidence] = useState(1.0);
    const [voiceLanguage, setVoiceLanguage] = useState('');

    // ── OCR State ───────────────────────────────────────────────────────────
    const [ocrProgress, setOcrProgress] = useState(0);
    const [ocrRunning, setOcrRunning] = useState(false);
    const [ocrRawText, setOcrRawText] = useState('');       // original noisy OCR output
    const [ocrCleanedText, setOcrCleanedText] = useState(''); // cleaned, editable by user
    const [ocrCategory, setOcrCategory] = useState(null);   // fuzzy-matched category
    const [ocrConfidence, setOcrConfidence] = useState(0);
    const [notification, setNotification] = useState(null); // { message, type }

    const mediaRecorder = useRef(null);
    const audioChunks = useRef([]);
    const recordingStartTime = useRef(null);
    const descriptionDebounce = useRef(null);

    const navigate = useNavigate();
    const { t } = useTranslation();

    const ZONES = Object.keys(GCC_ZONE_MAP);

    // ── 0. Sync area state with autoZone ────────────────────────────────────
    useEffect(() => {
        if (autoZone) {
            setArea(autoZone);
        } else {
            setArea('');
        }
    }, [autoZone]);

    // ── 1. Auto-extract from typed description ──────────────────────────────
    useEffect(() => {
        if (descriptionDebounce.current) clearTimeout(descriptionDebounce.current);
        descriptionDebounce.current = setTimeout(() => {
            if (description && description.trim().length > 5) {
                const result = extractLocationFromText(description);
                if (result.areaName && result.confidence > 0.5) updateDetected(result, 'text');
            }
        }, 600);
        return () => clearTimeout(descriptionDebounce.current);
    }, [description]);

    const updateDetected = (result, source) => {
        if (detectedAccepted) return;
        setDetectedLocation(result);
        setDetectedSource(source);
    };

    const showNotification = (message, type = 'success') => {
        setNotification({ message, type });
        setTimeout(() => setNotification(null), 4000);
    };

    // ── 2. Reverse geocode map pin (Nominatim — free, no API key) ──────────
    const reverseGeocode = async (lat, lng) => {
        setMapLoading(true);
        try {
            const res = await fetch(
                `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&addressdetails=1`,
                { headers: { 'Accept-Language': 'en' } }
            );
            const data = await res.json();
            const addr = data.address || {};
            const parts = [
                addr.road || addr.pedestrian || addr.footway,
                addr.suburb || addr.neighbourhood || addr.quarter,
                addr.city_district || addr.county,
                addr.city || addr.town || addr.village,
                addr.postcode
            ].filter(Boolean);
            const readable = parts.join(', ');
            setMapAddress(readable);

            // Auto-detect GCC zone from the full Nominatim address object
            const detectedZone = detectZoneFromAddress(addr);
            if (detectedZone) {
                setAutoZone(detectedZone);
            } else {
                setAutoZone(null); // couldn't determine zone
            }

            // Conflict check with text-detected location
            if (detectedAccepted && detectedLocation?.areaName) {
                const textZone = detectZoneFromAreaName(detectedLocation.areaName);
                if (textZone && detectedZone && textZone !== detectedZone) {
                    setMapAreaName(detectedZone || readable);
                    setShowConflictDialog(true);
                }
            }
        } catch (err) {
            console.warn('Reverse geocode failed:', err);
            setMapAddress(`${lat.toFixed(5)}, ${lng.toFixed(5)}`);
        } finally {
            setMapLoading(false);
        }
    };

    // ── 3. Map pin drop handler ─────────────────────────────────────────────
    const handleMapPick = (lat, lng) => {
        setMapPin({ lat, lng });
        setLocation(`${lat.toFixed(5)}, ${lng.toFixed(5)}`);
        setLocationError('');
        reverseGeocode(lat, lng);
    };

    // ── 4. Center map on user GPS ───────────────────────────────────────────
    const centerOnGps = () => {
        if (!navigator.geolocation) return;
        setMapLoading(true);
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const { latitude: lat, longitude: lng } = pos.coords;
                if (mapRef.current) mapRef.current.setView([lat, lng], 17);
                handleMapPick(lat, lng);
                setMapLoading(false);
            },
            () => { setMapLoading(false); }
        );
    };

    // ── 5. Voice recording + Backend STT (High Accuracy v3.0) ───────────────
    const transcribeBackend = async (audioBlob) => {
        setVoiceDetecting(true);
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'voice.wav');

            const response = await api.post('/stt/transcribe', formData);
            const data = response.data;
            setVoiceTranscript(data.transcription || '');
            setVoiceConfidence(data.confidence || 0.8);
            setVoiceLanguage(data.language_detected || 'Unknown');

            // Auto-extract location from the new transcript
            if (data.transcription) {
                const result = extractLocationFromText(data.transcription);
                if (result.areaName) updateDetected(result, 'voice');
            }
        } catch (err) {
            console.error('Backend STT failed:', err);
            showNotification(t('report.voiceError'), 'error');
        } finally {
            setVoiceDetecting(false);
        }
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder.current = new MediaRecorder(stream);
            audioChunks.current = [];
            recordingStartTime.current = Date.now();

            mediaRecorder.current.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunks.current.push(e.data);
            };

            mediaRecorder.current.onstop = () => {
                const duration = (Date.now() - recordingStartTime.current) / 1000;
                if (duration < 1.0) {
                    showNotification(t('report.voiceTooShort'), 'error');
                    setAudioURL(null);
                    setAudioFile(null);
                    setVoiceTranscript('');
                    return;
                }

                const blob = new Blob(audioChunks.current, { type: 'audio/wav' });
                if (blob.size === 0) {
                    showNotification(t('report.voiceError'), 'error');
                    return;
                }

                setAudioURL(URL.createObjectURL(blob));
                const file = new File([blob], `voice_${Date.now()}.wav`, { type: 'audio/wav' });
                setAudioFile(file);

                // Trigger backend transcription immediately
                transcribeBackend(blob);
            };

            mediaRecorder.current.start();
            setIsRecording(true);
        } catch (err) {
            console.error('Mic Error:', err);
            showNotification(t('report.micError'), 'error');
        }
    };

    const stopRecording = () => {
        if (mediaRecorder.current && isRecording) {
            mediaRecorder.current.stop();
            setIsRecording(false);
            mediaRecorder.current.stream.getTracks().forEach(t => t.stop());
        }
    };

    // ── 6. Image OCR (Full Pipeline: Preprocess → OCR → Clean → Fuzzy Match) ────
    const handlePaperComplaintUpload = async (file) => {
        setPaperComplaint(file);
        if (!file || !file.type.startsWith('image/')) return;
        setOcrRunning(true);
        setOcrProgress(0);
        setOcrRawText('');
        setOcrCleanedText('');
        setOcrCategory(null);
        setOcrConfidence(0);
        try {
            const { rawText, cleanedText, category, confidence, location } =
                await runOCRPipeline(file, setOcrProgress);

            setOcrRawText(rawText);
            setOcrCleanedText(cleanedText);
            setOcrCategory(category);
            setOcrConfidence(confidence);

            // Auto-fill description if it's empty
            if (!description.trim() && cleanedText.trim()) {
                setDescription(cleanedText);
            }

            // Location detection from cleaned text
            if (location.areaName) updateDetected(location, 'image');
        } catch (err) {
            console.error('OCR pipeline error:', err);
        } finally {
            setOcrRunning(false);
            setOcrProgress(0);
        }
    };

    // ── 7. Accept auto-detected location ───────────────────────────────────
    const acceptDetectedLocation = () => {
        if (!detectedLocation) return;
        setDetectedAccepted(true);
        setManualArea(detectedLocation.areaName);
        if (detectedLocation.landmark) setManualLandmark(detectedLocation.landmark);
        // Auto-detect GCC zone from area name
        const zone = detectZoneFromAreaName(detectedLocation.areaName);
        if (zone) setAutoZone(zone);
        setLocationError('');
    };

    const dismissDetection = () => { setDetectedLocation(null); setDetectedSource(null); };

    // ── 8. Conflict resolution ──────────────────────────────────────────────
    const resolveConflict = (choice) => {
        if (choice === 'text') {
            setLocationMode('manual');
            setManualArea(detectedLocation.areaName);
            if (detectedLocation.landmark) setManualLandmark(detectedLocation.landmark);
            const zone = detectZoneFromAreaName(detectedLocation.areaName);
            if (zone) setAutoZone(zone);
            setMapPin(null); setLocation(''); setMapAddress('');
        }
        setShowConflictDialog(false);
    };

    // ── 9. Validation ───────────────────────────────────────────────────────
    const hasLocation = () => {
        if (locationMode === 'map' && mapPin) return true;
        if (locationMode === 'manual' && manualArea.trim() && manualLandmark.trim()) return true;
        if (detectedAccepted && detectedLocation?.areaName && (manualLandmark.trim() || detectedLocation?.landmark)) return true;
        return false;
    };

    const buildFinalLocation = () => {
        if (locationMode === 'map' && mapPin) {
            const parts = [`${mapPin.lat.toFixed(5)}, ${mapPin.lng.toFixed(5)}`];
            if (mapAddress) parts.push(mapAddress);
            return parts.join(' | ');
        }
        const parts = [manualArea || detectedLocation?.areaName];
        if (manualLandmark) parts.push(`Near ${manualLandmark}`);
        if (manualPincode) {
            const cleanPin = manualPincode.split('.')[0].replace(/\D/g, '');
            if (cleanPin) parts.push(`PIN: ${cleanPin}`);
        }
        return parts.filter(Boolean).join(', ');
    };

    // ── 10. Submit ──────────────────────────────────────────────────────────
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!hasLocation()) {
            setLocationError('Please provide location details (Map pin or Area + Landmark).');
            return;
        }
        try {
            setLoading(true); setLocationError('');
            const formData = new FormData();
            const finalDescription = [voiceTranscript, description].filter(Boolean).join('\n\n');
            formData.append('description', finalDescription || '');
            formData.append('location', buildFinalLocation());
            formData.append('area', area);
            if (image) formData.append('image', image);
            if (audioFile) formData.append('audio', audioFile);
            if (paperComplaint) formData.append('paper_complaint', paperComplaint);
            const response = await api.post('/complaints/', formData);
            navigate(`/complaint/${response.data.id}`);
        } catch (err) {
            console.error('Submit error:', err);
        } finally {
            setLoading(false);
        }
    };

    const steps = [
        { id: 1, title: t('report.stepDetails'), icon: <PenTool size={18} /> },
        { id: 2, title: t('report.stepMedia'), icon: <Camera size={18} /> },
        { id: 3, title: t('report.stepSubmit'), icon: <MapPin size={18} /> }
    ];

    return (
        <div className="max-w-7xl mx-auto py-12 px-6 sm:px-12 space-y-12">
            {/* Notification Toast */}
            {notification && (
                <div className={`fixed top-24 right-8 z-[2000] px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-3 animate-slide-in text-white font-bold ${notification.type === 'success' ? 'bg-primary' : 'bg-red-500'
                    }`}>
                    {notification.type === 'success' ? <CheckCircle2 size={24} /> : <AlertTriangle size={24} />}
                    <span className="max-w-xs">{notification.message}</span>
                </div>
            )}

            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8">
                <h1 className="text-4xl font-extrabold text-secondary tracking-tight">{t('report.title')}</h1>
                <p className="text-secondary/60 font-medium max-w-xl mx-auto">{t('report.subtitle')}</p>
            </div>

            {/* Stepper */}
            <div className="flex items-center justify-center mb-16 relative px-4">
                <div className="absolute top-1/2 left-4 right-4 h-0.5 bg-gray-100 -translate-y-1/2 z-0" />
                <div className="relative z-10 flex justify-between w-full max-w-2xl">
                    {steps.map((s) => (
                        <div key={s.id} className="flex flex-col items-center gap-3">
                            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-500 border-2 ${step >= s.id ? 'bg-primary border-primary text-white scale-110 shadow-lg' : 'bg-white border-gray-100 text-gray-300'}`}>
                                {step > s.id ? <CheckCircle2 size={24} /> : s.icon}
                            </div>
                            <span className={`text-xs font-bold uppercase tracking-widest ${step >= s.id ? 'text-secondary' : 'text-gray-300'}`}>{s.title}</span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-12 items-start">
                <div className="lg:col-span-2 space-y-8 animate-fade-in-up">
                    <form onSubmit={handleSubmit} className="space-y-8">

                        {/* ── STEP 1 ── */}
                        {step === 1 && (
                            <div className="space-y-6">
                                <div className="bg-white rounded-3xl border border-gray-100 shadow-soft p-8 space-y-6">
                                    <label className="flex items-center gap-2 text-lg font-bold text-secondary">
                                        <Mic size={22} className="text-primary" />{t('report.voiceDescription')}
                                    </label>
                                    {!audioURL ? (
                                        <div className="space-y-4">
                                            <div className="flex flex-col sm:flex-row gap-4">
                                                <button type="button" onClick={isRecording ? stopRecording : startRecording}
                                                    className={`flex-1 h-20 rounded-2xl flex items-center justify-center gap-4 font-bold text-lg transition-all ${isRecording ? 'bg-red-500 text-white animate-pulse shadow-lg' : 'bg-gray-50 text-primary hover:bg-gray-100'}`}>
                                                    {isRecording ? <StopCircle size={32} /> : <Mic size={32} />}
                                                    {isRecording ? t('report.recordingActive') : t('report.recordVoice')}
                                                </button>
                                                <div className="relative flex-1">
                                                    <input type="file" id="audio-upload" accept="audio/*" hidden
                                                        onChange={(e) => { const f = e.target.files[0]; if (f) { setAudioFile(f); setAudioURL(URL.createObjectURL(f)); } }} />
                                                    <label htmlFor="audio-upload"
                                                        className="flex h-20 w-full items-center justify-center gap-4 bg-white border-2 border-dashed border-gray-200 text-gray-400 rounded-2xl cursor-pointer hover:border-primary hover:text-primary transition-all font-bold">
                                                        <Upload size={28} />{t('report.uploadFile')}
                                                    </label>
                                                </div>
                                            </div>
                                            <p className="text-center text-xs text-earth/30 font-bold uppercase tracking-tight italic">{t('report.supportedFormats')}</p>
                                        </div>
                                    ) : (
                                        <div className="bg-gray-50 p-6 rounded-2xl flex items-center gap-6 border border-gray-100">
                                            <div className="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center text-primary"><FileAudio size={24} /></div>
                                            <div className="flex-1 space-y-2">
                                                <p className="text-sm font-bold text-secondary truncate">{audioFile?.name || t('report.voiceDescription')}</p>
                                                <audio src={audioURL} controls className="w-full h-8" />
                                            </div>
                                            <button type="button" onClick={() => { setAudioURL(null); setAudioFile(null); setVoiceTranscript(''); }}
                                                className="p-2 text-red-400 hover:text-red-500 transition-colors"><Trash2 size={24} /></button>
                                        </div>
                                    )}
                                    {voiceDetecting && (
                                        <div className="flex items-center gap-2 text-primary text-xs font-bold animate-pulse">
                                            <Loader2 size={14} className="animate-spin" /> {t('report.processingAudio')}
                                        </div>
                                    )}
                                    {voiceTranscript && !voiceDetecting && (
                                        <div className="space-y-3">
                                            <div className="bg-blue-50 border border-blue-100 rounded-2xl p-4 space-y-3">
                                                <div className="flex items-center gap-2">
                                                    <div className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${voiceConfidence > 0.6 ? 'bg-blue-200 text-blue-700' : 'bg-orange-200 text-orange-700'}`}>
                                                        {voiceConfidence > 0.6 ? t('report.highConfidence') : t('report.lowConfidence')}
                                                    </div>
                                                    <span className="text-[10px] text-blue-400 font-bold ml-auto">{voiceLanguage} Detected</span>
                                                </div>
                                                <div className="space-y-1">
                                                    <p className="text-xs font-bold text-blue-800 flex items-center gap-1">
                                                        <Sparkles size={12} /> {t('report.voiceDetectedText')}
                                                    </p>
                                                    <textarea
                                                        className="w-full bg-white/50 border-none rounded-xl text-sm p-3 focus:ring-2 focus:ring-blue-300 transition-all font-medium text-blue-900"
                                                        rows={3}
                                                        value={voiceTranscript}
                                                        onChange={(e) => setVoiceTranscript(e.target.value)}
                                                    />
                                                    <p className="text-[10px] text-blue-400 italic font-medium px-1">{t('report.editManualTip')}</p>
                                                </div>
                                            </div>
                                            {voiceConfidence < 0.5 && (
                                                <div className="bg-orange-50 border border-orange-100 rounded-xl p-3 flex items-center gap-2 text-orange-700">
                                                    <AlertTriangle size={14} />
                                                    <p className="text-[10px] font-bold">{t('report.audioUnclearTip')}</p>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>

                                <div className="bg-white rounded-3xl border border-gray-100 shadow-soft p-8 space-y-4">
                                    <label className="text-lg font-bold text-secondary">{t('report.writtenDetails')}</label>
                                    <textarea rows="5" placeholder={t('report.writtenPlaceholder')} value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        className="form-input text-lg leading-relaxed resize-none p-6 w-full" />
                                </div>

                                <DetectionBanner detected={detectedLocation} source={detectedSource}
                                    onAccept={acceptDetectedLocation} onDismiss={dismissDetection} />

                                {detectedAccepted && (
                                    <div className="bg-green-50 border border-green-200 rounded-2xl p-3 flex items-center gap-3">
                                        <CheckCircle2 size={16} className="text-green-600" />
                                        <p className="text-sm font-bold text-green-700">✅ Location set: {manualArea}{manualLandmark && ` · Near ${manualLandmark}`}</p>
                                        <button type="button" onClick={() => { setDetectedAccepted(false); setManualArea(''); setManualLandmark(''); }}
                                            className="ml-auto text-xs text-green-600 font-bold underline">Change</button>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* ── STEP 2 ── */}
                        {step === 2 && (
                            <div className="space-y-8 animate-fade-in-up">
                                <div className="grid md:grid-cols-2 gap-8">
                                    <div className="glass-card p-8 bg-white/40 border-earth/10 space-y-6">
                                        <div className="flex items-center gap-2 text-lg font-bold text-secondary">
                                            <Camera size={22} className="text-primary" />{t('report.siteEvidence')}
                                        </div>
                                        <div className="relative h-64 flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-earth/20 bg-accent/30 overflow-hidden group">
                                            {image ? (
                                                <>
                                                    <img src={URL.createObjectURL(image)} className="w-full h-full object-cover" alt="Preview" />
                                                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                        <button onClick={() => setImage(null)} className="p-4 bg-red-500 rounded-full text-white shadow-xl"><Trash2 size={28} /></button>
                                                    </div>
                                                </>
                                            ) : (
                                                <label className="flex flex-col items-center gap-4 cursor-pointer text-earth/20 hover:text-primary transition-colors">
                                                    <div className="w-20 h-20 bg-white rounded-[2rem] shadow-premium flex items-center justify-center"><Camera size={40} /></div>
                                                    <span className="font-bold text-sm tracking-widest uppercase">{t('report.clickToCapture')}</span>
                                                    <input type="file" hidden accept="image/*" onChange={(e) => setImage(e.target.files[0])} />
                                                </label>
                                            )}
                                        </div>
                                    </div>

                                    <div className="glass-card p-8 bg-white/40 border-earth/10 space-y-6">
                                        <div className="flex items-center gap-2 text-lg font-bold text-secondary">
                                            <FileImage size={22} className="text-earth" />{t('report.paperComplaint')}
                                        </div>
                                        <div className="relative h-64 flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-earth/10 bg-accent/20 overflow-hidden group">
                                            {paperComplaint ? (
                                                <>
                                                    <img src={URL.createObjectURL(paperComplaint)} className="w-full h-full object-cover" alt="Doc Preview" />
                                                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                        <button onClick={() => { setPaperComplaint(null); setOcrRawText(''); setOcrCleanedText(''); setOcrCategory(null); }} className="p-4 bg-red-500 rounded-full text-white shadow-xl"><Trash2 size={28} /></button>
                                                    </div>
                                                </>
                                            ) : (
                                                <label className="flex flex-col items-center gap-4 cursor-pointer text-earth/20 hover:text-primary transition-colors px-10 text-center">
                                                    <div className="w-20 h-20 bg-white rounded-[2rem] shadow-premium flex items-center justify-center"><Upload size={32} /></div>
                                                    <span className="font-bold text-sm tracking-widest uppercase italic leading-tight">{t('report.dropScan')}</span>
                                                    <input type="file" hidden accept="image/*" onChange={(e) => e.target.files[0] && handlePaperComplaintUpload(e.target.files[0])} />
                                                </label>
                                            )}
                                        </div>
                                        {ocrRunning && (
                                            <div className="space-y-2">
                                                <div className="flex items-center gap-2 text-xs font-bold text-earth/50">
                                                    <ScanText size={14} className="animate-pulse text-primary" /> Reading document... {ocrProgress}%
                                                </div>
                                                <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                                    <div className="h-full bg-primary transition-all duration-300" style={{ width: `${ocrProgress}%` }} />
                                                </div>
                                            </div>
                                        )}
                                        {/* OCR Editable Preview + Category Suggestion */}
                                        {ocrCleanedText && !ocrRunning && (
                                            <div className="space-y-4">
                                                {/* Category Badge */}
                                                {ocrCategory && (
                                                    <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-xs font-bold ${ocrConfidence > 0.5 ? 'bg-green-50 border-green-200 text-green-700'
                                                        : 'bg-amber-50 border-amber-200 text-amber-700'
                                                        }`}>
                                                        <Sparkles size={13} />
                                                        AI Detected: <span className="font-extrabold">{ocrCategory}</span>
                                                        <span className="ml-auto text-[10px] opacity-70">~{Math.round(ocrConfidence * 100)}% confidence</span>
                                                    </div>
                                                )}

                                                {/* Editable OCR text */}
                                                <div className="space-y-1">
                                                    <p className="text-xs font-bold text-earth/40 uppercase tracking-widest flex items-center gap-1">
                                                        <ScanText size={12} /> Extracted Text — edit below if needed:
                                                    </p>
                                                    <textarea
                                                        rows={4}
                                                        value={ocrCleanedText}
                                                        onChange={(e) => {
                                                            setOcrCleanedText(e.target.value);
                                                            // Re-run category on edit
                                                            const { category, confidence } = fuzzyMatchCategory(e.target.value);
                                                            setOcrCategory(category);
                                                            setOcrConfidence(confidence);
                                                        }}
                                                        className="form-input text-sm text-secondary leading-relaxed resize-none p-4 w-full border-blue-200 focus:border-blue-400"
                                                    />
                                                    <div className="flex gap-2">
                                                        <button type="button"
                                                            onClick={() => setDescription(ocrCleanedText)}
                                                            className="px-4 py-1.5 bg-primary text-white text-xs font-bold rounded-xl hover:bg-primary/90 transition-colors">
                                                            ✅ Use as Complaint Description
                                                        </button>
                                                        {ocrRawText !== ocrCleanedText && (
                                                            <button type="button"
                                                                onClick={() => setOcrCleanedText(ocrRawText)}
                                                                className="px-4 py-1.5 bg-gray-100 text-gray-500 text-xs font-bold rounded-xl hover:bg-gray-200 transition-colors">
                                                                ↩ Show Raw OCR
                                                            </button>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <DetectionBanner detected={detectedLocation} source={detectedSource}
                                    onAccept={acceptDetectedLocation} onDismiss={dismissDetection} />
                            </div>
                        )}

                        {/* ── STEP 3: Location with Map ── */}
                        {step === 3 && (
                            <div className="space-y-8 animate-fade-in-up">
                                <div className="glass-card p-8 bg-white/40 border-earth/10 space-y-6">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2 text-lg font-bold text-secondary">
                                            <MapPin size={22} className="text-primary" />
                                            Location <span className="text-red-500 text-sm">*</span>
                                        </div>
                                        {/* Mode toggle */}
                                        <div className="flex gap-2 text-xs font-bold rounded-xl overflow-hidden border border-gray-100">
                                            <button type="button" onClick={() => setLocationMode('map')}
                                                className={`px-4 py-2 transition-all ${locationMode === 'map' ? 'bg-primary text-white' : 'bg-white text-gray-400 hover:text-primary'}`}>
                                                🗺️ Map
                                            </button>
                                            <button type="button" onClick={() => setLocationMode('manual')}
                                                className={`px-4 py-2 transition-all ${locationMode === 'manual' ? 'bg-primary text-white' : 'bg-white text-gray-400 hover:text-primary'}`}>
                                                ✏️ Manual
                                            </button>
                                        </div>
                                    </div>

                                    {/* ── MAP MODE ── */}
                                    {locationMode === 'map' && (
                                        <div className="space-y-4">
                                            <p className="text-xs text-earth/40 font-bold uppercase tracking-widest">
                                                Click anywhere on the map to drop a pin at the complaint location
                                            </p>

                                            {/* Map Container */}
                                            <div className="rounded-2xl overflow-hidden border-2 border-earth/10 shadow-soft" style={{ height: '340px' }}>
                                                <MapContainer
                                                    center={CHENNAI_CENTER}
                                                    zoom={12}
                                                    style={{ height: '100%', width: '100%' }}
                                                    ref={mapRef}
                                                >
                                                    <TileLayer
                                                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                                                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                                    />
                                                    <MapClickHandler onPick={handleMapPick} />
                                                    {mapPin && (
                                                        <Marker position={[mapPin.lat, mapPin.lng]} />
                                                    )}
                                                </MapContainer>
                                            </div>

                                            {/* Use My Location button */}
                                            <button type="button" onClick={centerOnGps}
                                                className="flex items-center gap-2 px-5 py-2.5 bg-white border border-primary/20 text-primary font-bold text-sm rounded-xl hover:bg-primary/5 transition-all shadow-sm">
                                                {mapLoading ? <Loader2 size={16} className="animate-spin" /> : <LocateFixed size={16} />}
                                                Use My Current Location
                                            </button>

                                            {/* Pin Result */}
                                            {mapPin && (
                                                <div className="bg-primary/5 border border-primary/10 rounded-2xl p-4 space-y-1">
                                                    <div className="flex items-center gap-2">
                                                        <MapPin size={16} className="text-primary shrink-0" />
                                                        <p className="text-sm font-bold text-secondary">
                                                            {mapLoading ? 'Getting address...' : mapAddress || `${mapPin.lat.toFixed(5)}, ${mapPin.lng.toFixed(5)}`}
                                                        </p>
                                                    </div>
                                                    <p className="text-xs text-earth/40 font-mono ml-6">{mapPin.lat.toFixed(5)}, {mapPin.lng.toFixed(5)}</p>
                                                </div>
                                            )}

                                            {!mapPin && (
                                                <div className="flex items-center gap-3 p-4 bg-amber-50 border border-amber-100 rounded-xl">
                                                    <AlertTriangle size={16} className="text-amber-500 shrink-0" />
                                                    <p className="text-xs font-bold text-amber-700">No pin placed yet. Click on the map above to mark the issue location.</p>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* ── MANUAL MODE ── */}
                                    {locationMode === 'manual' && (
                                        <div className="space-y-5 animate-fade-in-up">
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-widest text-earth/30 ml-1">Area Name <span className="text-red-500">*</span></label>
                                                <input type="text" value={manualArea} onChange={(e) => setManualArea(e.target.value)}
                                                    placeholder="e.g. Perambur, Anna Nagar, Velachery..."
                                                    className={`form-input h-14 font-bold text-secondary w-full ${locationError && !manualArea.trim() ? 'border-red-400 ring-2 ring-red-100' : ''}`} />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-widest text-earth/30 ml-1">
                                                    Landmark <span className="text-red-500">*</span>
                                                    <span className="ml-2 text-gray-300 normal-case font-normal">(Railway Station, Bus Stop, Hospital…)</span>
                                                </label>
                                                <input type="text" value={manualLandmark} onChange={(e) => setManualLandmark(e.target.value)}
                                                    placeholder="Near Railway Station / Bus Depot / School..."
                                                    className={`form-input h-14 text-secondary w-full ${locationError && !manualLandmark.trim() ? 'border-red-400 ring-2 ring-red-100' : ''}`} />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-widest text-earth/30 ml-1">Pincode <span className="text-gray-300">(Optional)</span></label>
                                                <input type="text" value={manualPincode} onChange={(e) => setManualPincode(e.target.value)}
                                                    placeholder="600011" maxLength={6} className="form-input h-14 font-mono text-secondary w-full" />
                                            </div>
                                        </div>
                                    )}

                                    {/* Auto-detection banner on Step 3 */}
                                    {detectedLocation && !detectedAccepted && (
                                        <DetectionBanner detected={detectedLocation} source={detectedSource}
                                            onAccept={acceptDetectedLocation} onDismiss={dismissDetection} />
                                    )}
                                    {detectedAccepted && (
                                        <div className="bg-green-50 border border-green-200 rounded-2xl p-4 flex items-center gap-3">
                                            <CheckCircle2 size={18} className="text-green-600" />
                                            <p className="text-sm font-bold text-green-700">✅ Using: {manualArea}{manualLandmark && ` · Near ${manualLandmark}`}</p>
                                        </div>
                                    )}

                                    {/* Zone Display (Read-only as per requirement) */}
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold uppercase tracking-widest text-earth/30 ml-1">{t('report.detectionZone')}</label>
                                        <div className={`form-input h-14 flex items-center px-4 font-extrabold transition-all ${autoZone ? 'bg-primary/5 text-primary border-primary/20' : 'bg-gray-50 text-gray-300 italic'}`}>
                                            {autoZone ? (
                                                <div className="flex items-center gap-2">
                                                    <Sparkles size={16} />
                                                    {autoZone}
                                                </div>
                                            ) : (
                                                "Detecting zone from location..."
                                            )}
                                        </div>
                                        <p className="text-[10px] text-earth/40 font-bold uppercase tracking-tight ml-1">
                                            {autoZone ? "✅ Administrative zone automatically assigned" : "⚠ Please select location on map to assign zone"}
                                        </p>
                                    </div>

                                    {locationError && (
                                        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
                                            <ShieldAlert size={18} className="text-red-500 shrink-0" />
                                            <p className="text-sm font-bold text-red-600">{locationError}</p>
                                        </div>
                                    )}
                                </div>

                                <div className="p-6 bg-gray-50 rounded-2xl border border-gray-100 flex gap-4 text-secondary/70">
                                    <ShieldAlert className="shrink-0 text-primary" />
                                    <p className="text-sm leading-relaxed font-medium">{t('report.verifyConcern')}</p>
                                </div>
                            </div>
                        )}

                        {/* Conflict Dialog */}
                        {showConflictDialog && (
                            <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
                                <div className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl space-y-6 animate-fade-in-up">
                                    <div className="flex items-center gap-3 text-amber-600">
                                        <AlertTriangle size={28} />
                                        <h3 className="font-bold text-lg text-secondary">Location Conflict</h3>
                                    </div>
                                    <p className="text-sm text-secondary/70 leading-relaxed">
                                        Your map pin is in <span className="font-bold text-secondary">{mapAreaName}</span>, but your complaint mentions <span className="font-bold text-primary">{detectedLocation?.areaName}</span>. Which should be used?
                                    </p>
                                    <div className="grid grid-cols-2 gap-4">
                                        <button type="button" onClick={() => resolveConflict('map')}
                                            className="p-4 rounded-2xl border-2 border-gray-100 hover:border-primary/30 transition-all text-center space-y-2">
                                            <MapPin size={24} className="mx-auto text-gray-400" />
                                            <p className="text-xs font-bold text-secondary">Map Location</p>
                                            <p className="text-[10px] text-gray-400">{mapAreaName}</p>
                                        </button>
                                        <button type="button" onClick={() => resolveConflict('text')}
                                            className="p-4 rounded-2xl border-2 border-primary/30 bg-primary/5 hover:border-primary transition-all text-center space-y-2">
                                            <Edit3 size={24} className="mx-auto text-primary" />
                                            <p className="text-xs font-bold text-secondary">Complaint Location</p>
                                            <p className="text-[10px] text-primary font-bold">{detectedLocation?.areaName}</p>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Navigation */}
                        <div className="flex justify-between pt-8 border-t border-earth/10">
                            {step > 1 ? (
                                <button type="button" onClick={() => setStep(step - 1)}
                                    className="px-8 py-4 text-gray-400 font-bold hover:text-secondary flex items-center gap-2 transition-all">
                                    <ChevronLeft size={20} /> {t('common.back')}
                                </button>
                            ) : <div />}

                            {step < 3 ? (
                                <button type="button" onClick={() => setStep(step + 1)}
                                    className="btn-primary group shadow-premium">
                                    {t('common.continue')} <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
                                </button>
                            ) : (
                                <button type="submit" disabled={loading || !hasLocation()}
                                    className={`btn-primary flex items-center gap-3 px-12 group shadow-premium ${!hasLocation() ? 'opacity-50 cursor-not-allowed' : ''}`}>
                                    {loading ? <Loader2 className="animate-spin" /> : <Send size={20} />}
                                    {loading ? t('report.submitting') : t('report.submit')}
                                </button>
                            )}
                        </div>
                    </form>
                </div>

                {/* Sidebar */}
                <aside className="lg:col-span-1 space-y-6 lg:sticky lg:top-32">
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-primary rounded-3xl blur-[2px] opacity-10 transition" />
                        <div className="relative bg-white border border-gray-100 rounded-3xl p-8 space-y-6 shadow-soft">
                            <div className="flex items-center gap-3 text-primary">
                                <Sparkles size={24} />
                                <h3 className="font-bold tracking-tight text-lg">AI Smart Analysis</h3>
                            </div>
                            <p className="text-sm text-earth/50 italic leading-relaxed">{t('report.aiNote')}</p>
                            <div className="space-y-4 pt-4 border-t border-earth/10">
                                <div className="space-y-2">
                                    <div className="flex justify-between text-xs font-bold uppercase tracking-widest text-gray-400">
                                        <span>Confidence</span><span>78%</span>
                                    </div>
                                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                                        <div className="h-full bg-primary w-[78%] animate-pulse" />
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    <div className="text-xs font-bold uppercase tracking-widest text-gray-400">Potential Routing</div>
                                    <div className="flex flex-wrap gap-2">
                                        <span className="px-3 py-1 bg-gray-100 text-secondary rounded-lg text-xs font-bold">Smart Infrastructure</span>
                                        <span className="px-3 py-1 bg-primary/10 text-primary rounded-lg text-xs font-bold">{area} Zone</span>
                                    </div>
                                </div>
                            </div>
                            <div className="bg-accent/20 p-4 rounded-xl space-y-3">
                                <div className="flex items-center gap-2 text-xs font-bold text-earth/30 uppercase tracking-tighter">
                                    <Info size={14} /> Validation Check
                                </div>
                                <div className="space-y-2">
                                    <ValidationItem check={description.length > 10} label="Clear Description" />
                                    <ValidationItem check={!!image || !!paperComplaint} label="Visual Proof" />
                                    <ValidationItem check={locationMode === 'map' ? !!mapPin : (manualArea.trim() && manualLandmark.trim()) || detectedAccepted} label="Location Provided" />
                                    <ValidationItem check={!!(mapPin || manualLandmark || detectedLocation?.landmark)} label="Landmark / Pin" />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="px-4 text-center">
                        <p className="text-[0.7rem] text-earth/40 font-bold uppercase tracking-tight leading-relaxed">
                            Official city platform. Powered by intelligent agent ecosystems.
                        </p>
                    </div>
                </aside>
            </div>
        </div>
    );
}

function ValidationItem({ check, label }) {
    return (
        <div className="flex items-center gap-2">
            <div className={`w-4 h-4 rounded-full flex items-center justify-center ${check ? 'bg-primary text-white' : 'bg-earth/10 text-transparent'}`}>
                {check && <CheckCircle2 size={10} />}
            </div>
            <span className={`text-xs font-bold ${check ? 'text-secondary' : 'text-earth/30'}`}>{label}</span>
        </div>
    );
}

export default ReportIssue;
