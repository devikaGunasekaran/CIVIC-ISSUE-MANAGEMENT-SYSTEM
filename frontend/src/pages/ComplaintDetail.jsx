import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import api from '../api';
import {
    Loader2, ArrowLeft, CheckCircle2, MapPin,
    XCircle, AlertTriangle, Sparkles, Navigation,
    FileAudio, FileImage, ExternalLink, LocateFixed, User2, MessageSquare,
    ShieldAlert, ShieldCheck, Zap, Send, Calendar, Camera, Building2, Clock, AlertCircle, ChevronRight
} from 'lucide-react';
import { formatLocation, formatAddress, formatZone } from '../utils/locationFormatter';

function ComplaintDetail() {
    const { id } = useParams();
    const [complaint, setComplaint] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const location = useLocation();
    const isSuccess = location.state?.success;
    const { t } = useTranslation();

    useEffect(() => {
        const fetchComplaint = async () => {
            try {
                const response = await api.get(`/complaints/${id}`);
                setComplaint(response.data);
            } catch (error) {
                console.error('Error fetching complaint:', error);
                navigate('/track');
            } finally {
                setLoading(false);
            }
        };
        fetchComplaint();
    }, [id, navigate]);

    if (loading) return (
        <div className="min-h-screen flex items-center justify-center bg-white">
            <div className="flex flex-col items-center gap-4">
                <Loader2 className="animate-spin text-primary" size={48} />
                <p className="text-gray-400 font-medium animate-pulse tracking-widest uppercase text-xs">{t('complaintDetail.initializing')}</p>
            </div>
        </div>
    );

    if (!complaint) return <div className="p-24 text-center text-gray-400">{t('complaintDetail.notFound')}</div>;

    const timeline = [
        { status: t('track.submitted'), icon: <Send size={16} />, active: true, date: t('common.latest') },
        { status: t('track.pending'), icon: <Sparkles size={16} />, active: complaint.status !== 'SUBMITTED', date: 'AI Analyzed' },
        { status: t('track.resolved'), icon: <CheckCircle2 size={16} />, active: complaint.status === 'RESOLVED', date: 'Resolution' }
    ];

    return (
        <div className="max-w-7xl mx-auto py-12 px-6 animate-fade-in-up">
            {/* Success Banner */}
            {isSuccess && (
                <div className="mb-10 bg-green-50 border border-green-100 rounded-3xl p-8 flex flex-col md:flex-row items-center gap-8 shadow-soft relative overflow-hidden">
                    <div className="absolute top-0 right-0 -mr-12 -mt-12 w-32 h-32 bg-primary/5 rounded-full blur-3xl"></div>
                    <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center text-primary shadow-sm border border-gray-100 shrink-0">
                        <CheckCircle2 size={32} />
                    </div>
                    <div className="space-y-2 flex-1 text-center md:text-left">
                        <h2 className="text-2xl font-bold text-secondary tracking-tight">{t('complaintDetail.successHeader')}</h2>
                        <p className="text-gray-500 font-medium">
                            {t('complaintDetail.refId')}: <span className="text-primary font-bold">#{complaint.id}</span> • {t('complaintDetail.etaLabel')}
                        </p>
                    </div>
                    <div className="flex gap-4">
                        <button onClick={() => navigate('/track')} className="btn-outline py-3 px-6">{t('complaintDetail.viewReports')}</button>
                    </div>
                </div>
            )}

            {/* Back Link */}
            <button
                onClick={() => navigate('/track')}
                className="group flex items-center gap-2 text-gray-400 font-bold hover:text-primary transition-colors mb-10 text-sm uppercase tracking-widest"
            >
                <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
                {t('complaintDetail.backTracking')}
            </button>

            <div className="grid lg:grid-cols-3 gap-12 items-start">
                {/* Main Content */}
                <div className="lg:col-span-2 space-y-10">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-2">
                        <div className="space-y-2">
                            <div className="flex items-center gap-3">
                                <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 tracking-tight">
                                    {complaint.category ? t(`categories.${complaint.category}`, { defaultValue: complaint.category }) : t('complaintDetail.generalIssue')}
                                </h1>
                                <span className="text-2xl text-gray-300 font-light italic">#{complaint.id}</span>
                            </div>
                            <div className="flex items-center gap-4 text-gray-400 font-medium text-sm">
                                <div className="flex items-center gap-1.5">
                                    <Calendar size={14} className="text-primary" />
                                    <span>{t('complaintDetail.capturedDate', { date: new Date(complaint.created_at).toLocaleDateString() })}</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <MapPin size={14} className="text-primary" />
                                    <span>{complaint.area || t('complaintDetail.metroZone')}</span>
                                </div>
                            </div>
                        </div>
                        <StatusBadge status={complaint.status} />
                    </div>

                    <div className="grid md:grid-cols-2 gap-10">
                        <div className="space-y-8">
                            <div className="space-y-3">
                                <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-gray-400 flex items-center gap-2">
                                    <MessageSquare size={14} className="text-primary" />
                                    {t('complaintDetail.citizenDescription')}
                                </h3>
                                <p className="text-lg text-gray-600 leading-relaxed font-medium">
                                    {complaint.description || t('complaintDetail.noDescription')}
                                </p>
                            </div>

                            <div className="flex items-center gap-6 p-6 bg-gray-50 rounded-[1.5rem] border border-gray-100">
                                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shadow-sm border ${getPriorityStyle(complaint.priority)}`}>
                                    <AlertTriangle size={24} />
                                </div>
                                <div>
                                    <h4 className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">{t('complaintDetail.systemPriority')}</h4>
                                    <PriorityBadge priority={complaint.priority} size="md" />
                                </div>
                            </div>
                        </div>

                        {/* Evidence Photo */}
                        <div className="relative group">
                            <div className="absolute -inset-2 bg-gradient-to-br from-green-100 to-transparent rounded-[2.5rem] opacity-40 blur-lg"></div>
                            <div className="relative aspect-square rounded-[2rem] overflow-hidden border-4 border-white shadow-soft">
                                {complaint.image_url ? (
                                    <img
                                        src={`http://localhost:8000/uploads/${complaint.image_url.split('/').pop()}`}
                                        alt="Evidence"
                                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                                    />
                                ) : (
                                    <div className="w-full h-full bg-gray-50 flex flex-col items-center justify-center text-gray-300 gap-4">
                                        <Camera size={48} />
                                        <span className="font-bold text-xs uppercase tracking-widest text-gray-400">{t('complaintDetail.noVisualEvidence')}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* AI Assessment Card */}
                    <div className="bg-white rounded-3xl p-10 border border-gray-100 shadow-soft relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-8 text-primary/5">
                            <Sparkles size={80} />
                        </div>
                        <div className="relative z-10 space-y-8">
                            <div className="flex items-center gap-3 text-primary">
                                <Sparkles size={24} />
                                <h3 className="text-2xl font-bold tracking-tight">{t('complaintDetail.aiDiagnostic')}</h3>
                            </div>

                            <div className="grid md:grid-cols-2 gap-10">
                                <div className="space-y-6">
                                    <div className="space-y-1">
                                        <h4 className="text-xs font-bold uppercase tracking-widest text-gray-400">{t('complaintDetail.routedDept')}</h4>
                                        <div className="flex items-center gap-3 text-secondary font-bold text-lg">
                                            <Building2 size={18} className="text-primary" />
                                            {complaint.category ? t(`categories.${complaint.category}`, { defaultValue: complaint.category }) : 'Environmental Services'}
                                        </div>
                                    </div>
                                    <div className="space-y-1">
                                        <h4 className="text-xs font-bold uppercase tracking-widest text-gray-400">{t('complaintDetail.aiLogic')}</h4>
                                        <p className="text-gray-500 italic text-sm leading-relaxed border-l-2 border-primary pl-4 py-1">
                                            "{complaint.ai_insight || t('complaintDetail.aiInProcess')}"
                                        </p>
                                    </div>
                                </div>
                                <div className="bg-white p-6 rounded-2xl shadow-sm border border-green-50 space-y-4">
                                    <div className="flex justify-between items-center text-xs font-bold uppercase tracking-widest text-gray-400">
                                        <span>{t('complaintDetail.infraScore')}</span>
                                        <span className="text-primary italic">{t('complaintDetail.infraSecure')}</span>
                                    </div>
                                    <div className="h-3 bg-gray-50 rounded-full overflow-hidden">
                                        <div className="h-full bg-primary w-[85%] animate-pulse rounded-full"></div>
                                    </div>
                                    <p className="text-[0.65rem] text-gray-400 leading-tight">
                                        {t('complaintDetail.infraDesc')}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Tracking Sidebar */}
                <aside className="space-y-10 lg:sticky lg:top-32">
                    <div className="bg-white border border-gray-100 p-10 space-y-10 shadow-soft rounded-3xl">
                        <h3 className="text-xl font-bold text-secondary tracking-tight border-b border-gray-50 pb-6">{t('complaintDetail.resolutionProgress')}</h3>

                        <div className="relative space-y-12">
                            {/* Vertical Line */}
                            <div className="absolute top-4 bottom-4 left-[2.45rem] w-0.5 bg-gray-100"></div>

                            {timeline.map((item, idx) => (
                                <div key={idx} className={`relative flex items-center gap-8 ${item.active ? 'opacity-100' : 'opacity-30'}`}>
                                    <div className={`w-20 h-20 rounded-2xl flex items-center justify-center z-10 shadow-sm border-2 ${item.active ? 'bg-primary border-primary text-white scale-110 shadow-lg shadow-green-100' : 'bg-white border-gray-100 text-gray-300'
                                        }`}>
                                        {item.icon}
                                    </div>
                                    <div className="space-y-1">
                                        <h4 className={`text-sm font-bold tracking-tight uppercase ${item.active ? 'text-secondary' : 'text-gray-400'}`}>
                                            {item.status}
                                        </h4>
                                        <p className="text-xs text-gray-400 font-medium italic">{item.date}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="pt-8 border-t border-gray-50 space-y-6">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 bg-accent rounded-xl flex items-center justify-center text-primary">
                                    <User2 size={18} />
                                </div>
                                <div>
                                    <h4 className="text-[0.65rem] font-bold uppercase tracking-widest text-gray-400">{t('complaintDetail.assignedOfficial')}</h4>
                                    <p className="text-sm font-bold text-secondary">N. Murali (Zonal Mgr)</p>
                                </div>
                            </div>
                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
                                        <LocateFixed size={20} />
                                    </div>
                                    <div className="flex flex-col">
                                        <p className="text-xs font-bold text-earth/40 uppercase tracking-widest">{t('complaint.location')}</p>
                                        <p className="text-sm font-bold text-secondary">{formatLocation(complaint.location)}</p>
                                    </div>
                                </div>
                                <div className="bg-gray-50/50 p-4 rounded-2xl border border-gray-100 flex items-start gap-3">
                                    <MapPin size={16} className="text-primary mt-0.5 shrink-0" />
                                    <p className="text-xs text-secondary font-medium italic leading-relaxed">
                                        {formatAddress(complaint.location)}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 bg-accent rounded-xl flex items-center justify-center text-primary">
                                    <Clock size={18} />
                                </div>
                                <div>
                                    <h4 className="text-[0.65rem] font-bold uppercase tracking-widest text-gray-400">{t('complaintDetail.nextAudit')}</h4>
                                    <p className="text-sm font-bold text-secondary">Tomorrow, 10:00 AM</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="p-8 bg-primary rounded-[2rem] text-white text-center space-y-4 shadow-xl shadow-green-200">
                        <p className="text-sm font-medium opacity-90">{t('complaintDetail.needHelp')}</p>
                        <button className="w-full py-4 bg-white text-primary font-bold rounded-2xl flex items-center justify-center gap-2 hover:bg-green-50 transition-colors group">
                            {t('complaintDetail.contactSupport')} <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
                        </button>
                    </div>
                </aside>
            </div>
        </div>
    );
}

function PriorityBadge({ priority, size = 'sm' }) {
    const { t } = useTranslation();
    const isCritical = priority === 'CRITICAL';
    const isHigh = priority === 'HIGH';

    const baseStyles = "inline-flex items-center gap-2 font-extrabold uppercase tracking-widest border transition-all duration-500 shadow-sm";
    const sizeStyles = size === 'md' ? "px-4 py-2 rounded-xl text-xs" : "px-3 py-1.5 rounded-lg text-[0.6rem]";

    const getColors = () => {
        const p = priority?.toUpperCase();
        switch (p) {
            case 'CRITICAL': return 'bg-red-600 text-white border-red-700 shadow-lg shadow-red-200 animate-pulse ring-2 ring-red-100 ring-offset-1';
            case 'HIGH': return 'bg-orange-500 text-white border-orange-600 shadow-md shadow-orange-100';
            case 'MEDIUM': return 'bg-amber-400 text-amber-950 border-amber-500 shadow-sm shadow-amber-50';
            case 'LOW': return 'bg-emerald-500 text-white border-emerald-600 shadow-sm shadow-emerald-50';
            default: return 'bg-gray-100 text-gray-500 border-gray-200';
        }
    };

    const getIcon = () => {
        const p = priority?.toUpperCase();
        const iconSize = size === 'md' ? 16 : 12;
        switch (p) {
            case 'CRITICAL': return <ShieldAlert size={iconSize} />;
            case 'HIGH': return <AlertTriangle size={iconSize} />;
            case 'MEDIUM': return <Zap size={iconSize} />;
            case 'LOW': return <ShieldCheck size={iconSize} />;
            default: return <AlertCircle size={iconSize} />;
        }
    };

    return (
        <span className={`${baseStyles} ${sizeStyles} ${getColors()}`}>
            {getIcon()}
            {priority ? t(`priorities.${priority}`, { defaultValue: priority }) : 'NORMAL'}
        </span>
    );
}

function StatusBadge({ status }) {
    const style = {
        SUBMITTED: 'bg-blue-50 text-blue-600 border-blue-100',
        PENDING: 'bg-orange-50 text-orange-600 border-orange-100',
        RESOLVED: 'bg-green-50 text-green-600 border-green-100',
        REJECTED: 'bg-red-50 text-red-600 border-red-100'
    };

    return (
        <div className={`px-6 py-2.5 rounded-full text-sm font-bold border-2 ${style[status] || 'bg-gray-100 text-gray-600 border-gray-200'} shadow-sm uppercase tracking-widest`}>
            {status}
        </div>
    );
}

function getPriorityStyle(priority) {
    switch (priority) {
        case 'CRITICAL': return 'bg-red-50 text-red-600 border-red-100';
        case 'HIGH': return 'bg-orange-50 text-orange-600 border-orange-100';
        case 'MEDIUM': return 'bg-yellow-50 text-yellow-600 border-yellow-100';
        case 'LOW': return 'bg-green-50 text-green-600 border-green-100';
        default: return 'bg-gray-50 text-gray-600 border-gray-100';
    }
}

function getPriorityTextColor(priority) {
    switch (priority) {
        case 'CRITICAL': return 'text-red-600';
        case 'HIGH': return 'text-orange-600';
        case 'MEDIUM': return 'text-yellow-600';
        case 'LOW': return 'text-green-600';
        default: return 'text-gray-600';
    }
}

export default ComplaintDetail;
