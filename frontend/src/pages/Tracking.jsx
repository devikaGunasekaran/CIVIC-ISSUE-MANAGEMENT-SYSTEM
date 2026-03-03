import { useEffect, useState } from 'react';
import api from '../api';
import {
    Loader2, Search, Filter, ChevronRight,
    Calendar, Tag, MoreHorizontal, LayoutGrid,
    List, AlertCircle, CheckCircle2, Clock, ShieldAlert, AlertTriangle, ShieldCheck, Zap
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

function Tracking() {
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeFilter, setActiveFilter] = useState('ALL');
    const { t } = useTranslation();

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

    const filteredComplaints = complaints.filter(c => {
        const matchesSearch = c.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            c.id.toString().includes(searchQuery);
        const matchesFilter = activeFilter === 'ALL' || c.status === activeFilter;
        return matchesSearch && matchesFilter;
    });

    const categories = ['ALL', 'SUBMITTED', 'PENDING', 'RESOLVED'];

    return (
        <div className="max-w-7xl mx-auto py-12 px-8 animate-fade-in-up">
            <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-8">
                <div className="space-y-4">
                    <h1 className="text-4xl font-bold text-secondary tracking-tight">{t('track.title')}</h1>
                    <p className="text-secondary/60 font-medium max-w-lg">
                        {t('track.subtitle')}
                    </p>
                </div>

                <div className="flex bg-gray-50 p-1.5 rounded-2xl border border-gray-100 shadow-soft">
                    {categories.map(cat => (
                        <button
                            key={cat}
                            onClick={() => setActiveFilter(cat)}
                            className={`px-6 py-2.5 rounded-xl text-xs font-bold uppercase tracking-widest transition-all ${activeFilter === cat
                                ? 'bg-primary text-white shadow-md'
                                : 'text-earth/40 hover:text-primary transition-colors'
                                }`}
                        >
                            {t(`track.${cat.toLowerCase()}`)}
                        </button>
                    ))}
                </div>
            </div>

            {/* Search and Stats Bar */}
            <div className="grid md:grid-cols-4 gap-6 mb-8">
                <div className="md:col-span-3 relative group">
                    <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-earth/30 group-focus-within:text-primary transition-colors" size={20} />
                    <input
                        type="text"
                        placeholder={t('track.searchPlaceholder')}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full h-16 pl-14 pr-8 bg-white border border-gray-100 rounded-2xl shadow-soft focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-gray-700 font-medium"
                    />
                </div>
                <div className="bg-primary rounded-2xl p-6 text-white flex items-center justify-between shadow-lg">
                    <div className="space-y-1">
                        <p className="text-[0.65rem] font-bold uppercase tracking-widest opacity-80">{t('track.totalReports')}</p>
                        <p className="text-3xl font-bold leading-none">{filteredComplaints.length}</p>
                    </div>
                    <Filter size={32} className="opacity-20" />
                </div>
            </div>

            {loading ? (
                <div className="py-32 flex flex-col items-center justify-center gap-6">
                    <Loader2 className="animate-spin text-primary" size={48} />
                    <p className="text-earth/40 font-bold uppercase tracking-widest text-xs animate-pulse font-mono">{t('track.syncing')}</p>
                </div>
            ) : filteredComplaints.length === 0 ? (
                <div className="py-32 bg-gray-50 rounded-3xl border border-dashed border-gray-200 flex flex-col items-center gap-6 text-center">
                    <div className="w-20 h-20 bg-white rounded-3xl flex items-center justify-center text-earth/20 shadow-soft">
                        <AlertCircle size={40} />
                    </div>
                    <div className="space-y-2">
                        <h3 className="text-xl font-bold text-secondary">{t('track.noComplaints')}</h3>
                        <p className="text-earth/50 text-sm max-w-xs mx-auto italic">
                            {t('track.noComplaintsHint')}
                        </p>
                    </div>
                </div>
            ) : (
                <div className="bg-white/90 backdrop-blur-md rounded-[2.5rem] shadow-premium border border-earth/10 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-accent/30 border-b border-earth/10">
                                    <th className="px-8 py-6 text-xs font-bold uppercase tracking-widest text-earth/30">{t('track.refId')}</th>
                                    <th className="px-8 py-6 text-xs font-bold uppercase tracking-widest text-earth/30">{t('track.category')}</th>
                                    <th className="px-8 py-6 text-xs font-bold uppercase tracking-widest text-earth/30">{t('track.date')}</th>
                                    <th className="px-8 py-6 text-xs font-bold uppercase tracking-widest text-earth/30">{t('admin.priority')}</th>
                                    <th className="px-8 py-6 text-xs font-bold uppercase tracking-widest text-earth/30">{t('track.status')}</th>
                                    <th className="px-8 py-6 text-xs font-bold uppercase tracking-widest text-earth/30 text-right">{t('track.action')}</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-earth/5">
                                {filteredComplaints.map((c) => (
                                    <tr key={c.id} className="group hover:bg-highlight/5 transition-colors">
                                        <td className="px-8 py-8">
                                            <span className="text-sm font-mono font-bold text-earth/20 group-hover:text-primary transition-colors">#{c.id}</span>
                                        </td>
                                        <td className="px-8 py-8">
                                            <div className="flex items-center gap-4">
                                                <div className="w-10 h-10 bg-accent rounded-xl flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                                                    <Tag size={18} />
                                                </div>
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-bold text-secondary">
                                                        {c.category ? t(`categories.${c.category}`, { defaultValue: c.category }) : 'General'}
                                                    </span>
                                                    <span className="text-[0.65rem] text-earth/40 font-medium italic truncate max-w-[200px]">
                                                        {c.description?.substring(0, 40)}...
                                                    </span>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-8 py-8">
                                            <div className="flex items-center gap-2 text-sm text-earth/50 font-medium">
                                                <Calendar size={14} className="text-earth/20" />
                                                {new Date(c.created_at).toLocaleDateString()}
                                            </div>
                                        </td>
                                        <td className="px-8 py-8">
                                            <PriorityBadge priority={c.priority} />
                                        </td>
                                        <td className="px-8 py-8">
                                            <StatusBadge status={c.status} />
                                        </td>
                                        <td className="px-8 py-8 text-right">
                                            <Link
                                                to={`/complaint/${c.id}`}
                                                className="inline-flex items-center justify-center w-12 h-12 bg-white border border-earth/10 rounded-xl text-earth/40 hover:bg-primary hover:text-white hover:border-primary transition-all shadow-sm active:scale-95"
                                            >
                                                <ChevronRight size={20} />
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="bg-accent/30 px-8 py-4 border-t border-earth/10">
                        <p className="text-[0.65rem] text-earth/40 font-bold uppercase tracking-widest flex items-center gap-2">
                            <Clock size={12} /> {t('track.liveSync')}
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}

function PriorityBadge({ priority, size = 'sm' }) {
    const { t } = useTranslation();
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
    const styles = {
        SUBMITTED: 'bg-blue-50 text-blue-700 border-blue-100',
        PENDING: 'bg-highlight/20 text-earth border-highlight/30',
        RESOLVED: 'bg-primary/10 text-primary border-primary/20',
        REJECTED: 'bg-red-50 text-red-700 border-red-100'
    };

    return (
        <span className={`px-4 py-1.5 rounded-full text-[0.65rem] font-bold border ${styles[status] || 'bg-accent text-earth/50 border-earth/10'} uppercase tracking-widest shadow-sm transition-colors`}>
            {status}
        </span>
    );
}

export default Tracking;
