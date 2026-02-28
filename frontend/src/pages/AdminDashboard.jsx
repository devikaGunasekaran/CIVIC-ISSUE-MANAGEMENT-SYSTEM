import { useEffect, useState } from 'react';
import api from '../api';
import {
    Loader2, Filter, AlertCircle, CheckCircle2,
    Search, Download, ExternalLink, RefreshCw,
    MoreVertical, X, Bell, MapPin, Sparkles, ArrowUpRight,
    ChevronRight, ShieldAlert, AlertTriangle, ShieldCheck, Zap, FileText,
    TrendingUp, Settings, Clock
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, LineChart, Line,
    AreaChart, Area, Cell, PieChart, Pie
} from 'recharts';
import { parseLocation, formatLocation, formatAddress } from '../utils/locationFormatter';

function AdminDashboard() {
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filterStatus, setFilterStatus] = useState('ALL');
    const [filterPriority, setFilterPriority] = useState('ALL');
    const [selectedComplaint, setSelectedComplaint] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [notification, setNotification] = useState(null);
    const [filterZone, setFilterZone] = useState('ALL');
    const [sortOrder, setSortOrder] = useState('latest');
    const { t } = useTranslation();

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
            showNotification(t('common.error'), 'error');
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
            showNotification(t('complaintDetail.successMessage'), 'success');
        } catch (error) {
            showNotification(t('common.error'), 'error');
        }
    };

    const showNotification = (message, type) => {
        setNotification({ message, type });
        setTimeout(() => setNotification(null), 3000);
    };

    const filteredComplaints = complaints
        .filter(c => {
            const matchesStatus = filterStatus === 'ALL' || c.status === filterStatus;
            const matchesPriority = filterPriority === 'ALL' || (c.priority && c.priority.toUpperCase() === filterPriority);
            const matchesZone = filterZone === 'ALL' || c.area === filterZone;
            const matchesSearch = searchQuery === '' ||
                c.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                c.location.toLowerCase().includes(searchQuery.toLowerCase()) ||
                (c.category && t(`categories.${c.category}`, { defaultValue: c.category }).toLowerCase().includes(searchQuery.toLowerCase())) ||
                (c.area && c.area.toLowerCase().includes(searchQuery.toLowerCase()));
            return matchesStatus && matchesPriority && matchesZone && matchesSearch;
        })
        .sort((a, b) => {
            const dateA = new Date(a.created_at);
            const dateB = new Date(b.created_at);
            return sortOrder === 'latest' ? dateB - dateA : dateA - dateB;
        });

    const uniqueZones = [...new Set(complaints.map(c => c.area).filter(Boolean))];

    // Chart Data Preparation
    const categoryData = complaints.reduce((acc, c) => {
        const cat = c.category || 'General';
        const existing = acc.find(item => item.name === cat);
        if (existing) existing.value++;
        else acc.push({ name: cat, value: 1 });
        return acc;
    }, []);

    const statusStats = {
        total: complaints.length,
        submitted: complaints.filter(c => c.status === 'SUBMITTED').length,
        inProgress: complaints.filter(c => c.status === 'IN_PROGRESS').length,
        resolved: complaints.filter(c => c.status === 'RESOLVED').length
    };

    const COLORS = ['#5E7D32', '#92A64E', '#435929', '#717A44', '#76632B'];

    return (
        <div className="max-w-7xl mx-auto py-10 px-8 space-y-12 animate-fade-in-up bg-white">
            {/* Notification Toast */}
            {notification && (
                <div className={`fixed top-24 right-8 z-[2000] px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-3 animate-slide-in text-white font-bold ${notification.type === 'success' ? 'bg-primary' : 'bg-red-500'
                    }`}>
                    {notification.type === 'success' ? <CheckCircle2 size={24} /> : <AlertCircle size={24} />}
                    {notification.message}
                </div>
            )}

            {/* Header Section */}
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                <div className="space-y-2">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white shadow-lg">
                            <TrendingUp size={24} />
                        </div>
                        <h1 className="text-3xl font-bold text-secondary tracking-tight">
                            {adminArea ? `${adminArea} ${t('admin.zoneDashboard')}` : t('admin.mainDashboard')}
                        </h1>
                    </div>
                    <p className="text-earth/50 font-medium ml-1">
                        {t('admin.dashboardSubtitle')} • {new Date().toLocaleDateString('en-GB')}
                    </p>
                </div>

                <div className="flex items-center gap-4">
                    <button className="p-3 bg-white border border-earth/10 rounded-xl text-earth/40 hover:text-primary hover:border-primary transition-all shadow-sm">
                        <Download size={20} />
                    </button>
                    <button className="p-3 bg-white border border-earth/10 rounded-xl text-earth/40 hover:text-primary hover:border-primary transition-all shadow-sm">
                        <Settings size={20} />
                    </button>
                    <button className="btn-primary flex items-center gap-3 px-6">
                        <FileText size={20} />
                        {t('admin.exportReports')}
                    </button>
                </div>
            </div>

            {/* Key Performance Indicators */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    label={t('track.totalComplaints')}
                    value={statusStats.total}
                    icon={<FileText size={28} />}
                    trend="+12%"
                    color="primary"
                />
                <StatCard
                    label={t('statuses.SUBMITTED')}
                    value={statusStats.submitted}
                    icon={<Clock size={28} />}
                    trend="-5%"
                    color="blue"
                />
                <StatCard
                    label={t('statuses.IN_PROGRESS')}
                    value={statusStats.inProgress}
                    icon={<Loader2 size={28} />}
                    trend="+2%"
                    color="amber"
                />
                <StatCard
                    label={t('statuses.RESOLVED')}
                    value={statusStats.resolved}
                    icon={<CheckCircle2 size={28} />}
                    trend="+18%"
                    color="green"
                />
            </div>

            {/* Charts Section */}
            <div className="grid lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 bg-white rounded-3xl border border-gray-100 p-10 shadow-soft space-y-8">
                    <div className="flex items-center justify-between">
                        <h3 className="text-xl font-bold text-secondary tracking-tight">{t('admin.frequencyTrends')}</h3>
                        <select className="bg-gray-50 border-none outline-none text-xs font-bold uppercase tracking-widest text-gray-400 rounded-lg px-3 py-1.5 cursor-pointer">
                            <option>{t('admin.last7Days')}</option>
                            <option>{t('admin.last30Days')}</option>
                        </select>
                    </div>
                    <div className="h-[350px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={complaints.slice(0, 7).map((c, i) => ({ name: `${t('admin.day')} ${i + 1}`, value: Math.floor(Math.random() * 20) + 10 }))}>
                                <defs>
                                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#5E7D32" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#5E7D32" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2EFDA" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#717A44', fontSize: 12 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#717A44', fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#fff', borderRadius: '16px', border: '1px solid #E2EFDA', boxShadow: '0 10px 30px rgba(67, 89, 41, 0.1)' }}
                                />
                                <Area type="monotone" dataKey="value" stroke="#5E7D32" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="lg:col-span-1 bg-white rounded-3xl border border-gray-100 p-10 shadow-soft space-y-8">
                    <h3 className="text-xl font-bold text-secondary tracking-tight">{t('admin.categoryDistribution')}</h3>
                    <div className="h-[300px] w-full relative">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={categoryData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={90}
                                    paddingAngle={8}
                                    dataKey="value"
                                >
                                    {categoryData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
                            <p className="text-2xl font-bold text-secondary">{statusStats.total}</p>
                            <p className="text-[0.65rem] font-bold text-earth/30 uppercase tracking-widest">{t('admin.reports')}</p>
                        </div>
                    </div>
                    <div className="space-y-4 pt-4 border-t border-earth/10">
                        {categoryData.slice(0, 3).map((item, i) => (
                            <div key={i} className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }}></div>
                                    <span className="text-sm font-bold text-earth/60 truncate max-w-[140px]">{t(`categories.${item.name}`, { defaultValue: item.name })}</span>
                                </div>
                                <span className="text-sm font-bold text-secondary">{item.value}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Controls and Filters */}
            <div className="bg-white rounded-3xl border border-gray-100 shadow-soft p-10 space-y-8">
                <div className="flex flex-col lg:flex-row lg:items-center gap-6">
                    <div className="relative flex-1 group">
                        <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-earth/30 group-focus-within:text-primary transition-colors" size={20} />
                        <input
                            type="text"
                            placeholder={t('common.searchPlaceholder')}
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full h-14 pl-14 pr-8 bg-accent/20 border border-earth/10 rounded-2xl focus:ring-2 focus:ring-primary/10 transition-all font-medium text-gray-700 outline-none"
                        />
                    </div>

                    <div className="flex flex-wrap items-center gap-4">
                        <FilterSelect
                            value={filterStatus}
                            onChange={setFilterStatus}
                            options={['ALL', 'SUBMITTED', 'IN_PROGRESS', 'RESOLVED']}
                            label={t('common.allStatus')}
                            translationPrefix="statuses"
                        />
                        <FilterSelect
                            value={filterZone}
                            onChange={setFilterZone}
                            options={['ALL', ...uniqueZones]}
                            label={t('common.allZones')}
                        />
                        <FilterSelect
                            value={filterPriority}
                            onChange={setFilterPriority}
                            options={['ALL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']}
                            label={t('common.allPriorities')}
                            translationPrefix="priorities"
                        />
                        <select
                            value={sortOrder}
                            onChange={(e) => setSortOrder(e.target.value)}
                            className="h-14 px-6 bg-accent/20 border border-earth/10 rounded-2xl text-sm font-bold text-secondary outline-none cursor-pointer"
                        >
                            <option value="latest">{t('common.latest')}</option>
                            <option value="oldest">{t('common.oldest')}</option>
                        </select>
                    </div>
                </div>

                {/* Complaints Data Table */}
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-earth/5">
                                <th className="px-6 py-4 text-xs font-bold uppercase tracking-[0.2em] text-earth/20">{t('admin.complaintNum')}</th>
                                <th className="px-6 py-4 text-xs font-bold uppercase tracking-[0.2em] text-earth/20">{t('admin.details')}</th>
                                <th className="px-6 py-4 text-xs font-bold uppercase tracking-[0.2em] text-earth/20">{t('admin.geography')}</th>
                                <th className="px-6 py-4 text-xs font-bold uppercase tracking-[0.2em] text-earth/20">{t('admin.priority')}</th>
                                <th className="px-6 py-4 text-xs font-bold uppercase tracking-[0.2em] text-earth/20">{t('admin.status')}</th>
                                <th className="px-6 py-4 text-xs font-bold uppercase tracking-[0.2em] text-earth/20 text-right">{t('admin.actions')}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-earth/5">
                            {loading ? (
                                <tr>
                                    <td colSpan="6" className="py-20 text-center">
                                        <Loader2 className="animate-spin text-primary inline-block mb-4" size={40} />
                                        <p className="text-earth/30 font-bold uppercase tracking-widest text-xs font-mono">{t('admin.loadingData')}</p>
                                    </td>
                                </tr>
                            ) : filteredComplaints.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="py-20 text-center">
                                        <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center text-gray-300 mx-auto mb-4">
                                            <AlertCircle size={32} />
                                        </div>
                                        <p className="text-gray-400 font-bold">{t('admin.noMatches')}</p>
                                    </td>
                                </tr>
                            ) : (
                                filteredComplaints.map((c) => (
                                    <tr key={c.id} className="group hover:bg-green-50/20 transition-all">
                                        <td className="px-6 py-6">
                                            <span className="text-sm font-mono font-bold text-primary italic">#{c.id}</span>
                                        </td>
                                        <td className="px-6 py-6">
                                            <div className="space-y-1">
                                                <p className="text-sm font-bold text-secondary">
                                                    {c.category ? t(`categories.${c.category}`, { defaultValue: c.category }) : 'General'}
                                                </p>
                                                <p className="text-xs text-gray-400 max-w-[250px] truncate leading-relaxed">
                                                    {c.description}
                                                </p>
                                            </div>
                                        </td>
                                        <td className="px-6 py-6">
                                            <div className="space-y-1">
                                                <div className="flex items-center gap-1.5 text-xs text-gray-700 font-bold">
                                                    <MapPin size={12} className="text-primary" />
                                                    {c.area || 'Metro'}
                                                </div>
                                                <p className="text-[0.65rem] text-gray-400 font-mono italic">
                                                    {formatLocation(c.location)}
                                                </p>
                                            </div>
                                        </td>
                                        <td className="px-6 py-6">
                                            <PriorityBadge priority={c.priority} />
                                        </td>
                                        <td className="px-6 py-6">
                                            <StatusCapsule status={c.status} />
                                        </td>
                                        <td className="px-6 py-6 text-right">
                                            <button
                                                onClick={() => setSelectedComplaint(c)}
                                                className="inline-flex items-center justify-center w-10 h-10 bg-white border border-gray-100 rounded-xl text-gray-400 hover:text-primary hover:border-primary hover:bg-green-50 transition-all shadow-sm"
                                            >
                                                <ChevronRight size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Multi-feature Admin Modal */}
            {selectedComplaint && (
                <div className="fixed inset-0 z-[3000] flex items-center justify-center p-6 sm:p-12 animate-fade-in">
                    <div className="absolute inset-0 bg-secondary/60" onClick={() => setSelectedComplaint(null)}></div>
                    <div className="relative bg-white w-full max-w-5xl max-h-full rounded-3xl shadow-2xl overflow-hidden flex flex-col md:flex-row animate-scale-in">
                        {/* Media Sidebar */}
                        <div className="w-full md:w-2/5 bg-gray-50 border-r border-gray-100 overflow-hidden relative group">
                            {selectedComplaint.image_url ? (
                                <img
                                    src={`http://localhost:8000/uploads/${selectedComplaint.image_url.split('/').pop()}`}
                                    className="w-full h-64 md:h-full object-cover"
                                    alt="Verification"
                                />
                            ) : (
                                <div className="h-64 md:h-full flex flex-col items-center justify-center text-earth/20 gap-4">
                                    <MapPin size={64} className="opacity-10" />
                                    <p className="text-xs font-bold uppercase tracking-widest italic">Digital Geotag Locked</p>
                                </div>
                            )}
                            <div className="absolute top-6 left-6 p-4 bg-white border border-gray-100 rounded-2xl shadow-premium space-y-1">
                                <p className="text-[0.65rem] font-bold text-gray-400 uppercase tracking-widest">Capture Sync</p>
                                <p className="text-xs font-bold text-secondary">{new Date(selectedComplaint.created_at).toLocaleString()}</p>
                            </div>
                        </div>

                        {/* Content & Control Panel */}
                        <div className="flex-1 p-10 md:p-14 overflow-y-auto space-y-10">
                            <div className="flex justify-between items-start">
                                <div className="space-y-1">
                                    <p className="text-xs font-bold text-primary uppercase tracking-widest italic tracking-tighter">{t('admin.managementInterface')}</p>
                                    <h2 className="text-3xl font-bold text-secondary tracking-tight">#{selectedComplaint.id} {t('admin.details')}</h2>
                                </div>
                                <button onClick={() => setSelectedComplaint(null)} className="p-3 bg-accent text-earth/30 rounded-2xl hover:bg-earth/10 transition-colors"><X size={20} /></button>
                            </div>

                            <div className="grid sm:grid-cols-2 gap-10">
                                <div className="space-y-6">
                                    <div className="space-y-4">
                                        <div className="space-y-2">
                                            <label className="text-xs font-bold uppercase tracking-widest text-earth/30">{t('admin.categorization')}</label>
                                            <p className="text-lg font-bold text-secondary flex items-center gap-2">
                                                <FileText size={18} className="text-primary" />
                                                {t(`categories.${selectedComplaint.category}`, { defaultValue: selectedComplaint.category })}
                                            </p>
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-xs font-bold uppercase tracking-widest text-gray-400">Current Priority</label>
                                            <div>
                                                <PriorityBadge priority={selectedComplaint.priority} size="md" />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold uppercase tracking-widest text-gray-400">{t('admin.citizenDescription')}</label>
                                        <p className="text-sm text-gray-600 leading-relaxed italic border-l-2 border-primary/20 pl-4">
                                            "{selectedComplaint.description || 'No digital metadata provided by citizen.'}"
                                        </p>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold uppercase tracking-widest text-gray-400">Location Details</label>
                                        <div className="p-4 bg-gray-50 rounded-2xl border border-gray-100 space-y-2">
                                            <p className="text-xs font-bold text-secondary flex items-center gap-2">
                                                <MapPin size={14} className="text-primary" />
                                                {formatLocation(selectedComplaint.location)}
                                            </p>
                                            <p className="text-xs text-gray-500 italic">
                                                {formatAddress(selectedComplaint.location)}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-8 bg-green-50/30 p-8 rounded-3xl border border-green-50">
                                    <div className="space-y-4">
                                        <h4 className="text-sm font-bold text-secondary flex items-center gap-2">
                                            <Bell size={16} className="text-primary" />
                                            {t('admin.operationalOverride')}
                                        </h4>
                                        <select
                                            value={selectedComplaint.status}
                                            onChange={(e) => handleStatusUpdate(selectedComplaint.id, e.target.value)}
                                            className="w-full h-14 px-6 bg-white border border-gray-100 rounded-2xl text-sm font-bold text-secondary focus:ring-2 focus:ring-primary/20 outline-none shadow-sm cursor-pointer"
                                        >
                                            <option value="SUBMITTED">{t('statuses.SUBMITTED')}</option>
                                            <option value="IN_PROGRESS">{t('statuses.IN_PROGRESS')}</option>
                                            <option value="RESOLVED">{t('statuses.RESOLVED')}</option>
                                        </select>
                                    </div>

                                    <div className="pt-6 border-t border-earth/10 space-y-4">
                                        <p className="text-xs text-earth/30 italic">{t('admin.aiInsightLabel')}</p>
                                        <div className="p-4 bg-white rounded-2xl shadow-sm border border-green-50 flex items-start gap-3">
                                            <Sparkles size={16} className="text-primary shrink-0 mt-0.5" />
                                            <p className="text-xs font-medium text-secondary leading-relaxed uppercase tracking-tighter">
                                                {selectedComplaint.ai_insight || 'Cross-referencing historical infrastructure health records for this zone.'}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-4 pt-4">
                                <button className="flex-1 bg-primary py-4 rounded-2xl text-white font-bold flex items-center justify-center gap-3 shadow-lg shadow-green-100 hover:scale-[1.02] transition-transform">
                                    <ArrowUpRight size={20} /> {t('admin.deployTeam')}
                                </button>
                                <button className="px-8 py-4 bg-gray-50 text-gray-600 font-bold rounded-2xl hover:bg-gray-100 transition-colors">{t('admin.notifyCitizen')}</button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function StatCard({ label, value, icon, trend, color }) {
    const variants = {
        primary: 'text-primary bg-primary/10',
        blue: 'text-blue-600 bg-blue-50',
        amber: 'text-amber-600 bg-amber-50',
        green: 'text-emerald-700 bg-emerald-50'
    };

    return (
        <div className="bg-white p-8 border border-gray-100 rounded-3xl shadow-soft flex items-start justify-between relative overflow-hidden group hover:shadow-premium transition-all duration-300">
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-125 transition-transform duration-1000">
                {icon}
            </div>
            <div className="space-y-4 relative z-10">
                <div className={`p-3.5 rounded-2xl inline-block ${variants[color]}`}>
                    {icon}
                </div>
                <div className="space-y-1">
                    <h4 className="text-[0.65rem] font-bold uppercase tracking-[0.2em] text-gray-400">
                        {label}
                    </h4>
                    <div className="flex items-end gap-3">
                        <p className="text-4xl font-bold text-secondary tracking-tight">{value}</p>
                        <span className={`text-xs font-bold mb-1.5 ${trend.startsWith('+') ? 'text-primary' : 'text-red-500'}`}>
                            {trend}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}

function FilterSelect({ value, onChange, options, label, translationPrefix }) {
    const { t } = useTranslation();
    return (
        <select
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="h-14 px-6 bg-gray-50 border border-gray-100 rounded-2xl text-sm font-bold text-secondary outline-none cursor-pointer hover:border-primary/20 transition-colors"
        >
            <option value="ALL">{label}</option>
            {options.filter(o => o !== 'ALL').map(opt => (
                <option key={opt} value={opt}>
                    {translationPrefix ? t(`${translationPrefix}.${opt}`, { defaultValue: opt }) : opt}
                </option>
            ))}
        </select>
    );
}

function StatusCapsule({ status }) {
    const styles = {
        SUBMITTED: 'bg-blue-50 text-blue-600 border-blue-100 shadow-blue-50',
        IN_PROGRESS: 'bg-highlight/20 text-earth border-highlight/30 shadow-highlight/10',
        RESOLVED: 'bg-primary/10 text-primary border-primary/20 shadow-primary/5',
        REJECTED: 'bg-red-50 text-red-600 border-red-100 shadow-red-50'
    };

    return (
        <div className={`px-4 py-2 rounded-xl text-[0.65rem] font-bold border-2 ${styles[status] || styles.SUBMITTED} uppercase tracking-widest shadow-sm inline-flex items-center gap-2`}>
            {status === 'RESOLVED' && <CheckCircle2 size={12} />}
            {status}
        </div>
    );
}

function PriorityBadge({ priority, size = 'sm' }) {
    const { t } = useTranslation();
    const isCritical = priority === 'CRITICAL';
    const isHigh = priority === 'HIGH';
    const isMedium = priority === 'MEDIUM';

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
        const iconSize = size === 'md' ? 18 : 14;
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

function getPriorityStyle(priority) {
    switch (priority) {
        case 'CRITICAL': return 'bg-red-50 text-red-600 border-red-100';
        case 'HIGH': return 'bg-orange-50 text-orange-600 border-orange-100';
        case 'MEDIUM': return 'bg-amber-50 text-amber-600 border-amber-100';
        case 'LOW': return 'bg-green-50 text-emerald-600 border-green-100';
        default: return 'bg-white text-gray-300 border-gray-100';
    }
}

export default AdminDashboard;
