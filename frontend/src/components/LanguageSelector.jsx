import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

function LanguageSelector() {
    const { i18n } = useTranslation();
    const currentLang = i18n.language?.startsWith('ta') ? 'ta' : 'en';

    const toggle = () => {
        const next = currentLang === 'en' ? 'ta' : 'en';
        i18n.changeLanguage(next);
        document.documentElement.lang = next;
    };

    return (
        <button
            onClick={toggle}
            title="Switch Language / மொழி மாற்று"
            className={`
                flex items-center gap-2.5 px-4 py-2 rounded-xl font-bold text-xs uppercase tracking-widest
                transition-all duration-300 shadow-sm border
                ${currentLang === 'en'
                    ? 'bg-white text-secondary border-gray-100 hover:border-primary/50 hover:text-primary shadow-soft'
                    : 'bg-primary text-white border-primary shadow-lg shadow-green-100/50 hover:opacity-90'
                }
            `}
            style={{ fontFamily: currentLang === 'ta' ? "'Noto Sans Tamil', sans-serif" : 'inherit' }}
        >
            <Globe size={14} className={currentLang === 'en' ? 'text-primary' : 'text-white'} />
            <span className="flex items-center gap-1.5">
                {currentLang === 'en' ? (
                    <>
                        <span>EN</span>
                        <span className="opacity-30">|</span>
                        <span className="font-normal opacity-70">தமிழ்</span>
                    </>
                ) : (
                    <>
                        <span className="font-normal opacity-90">தமிழ்</span>
                        <span className="opacity-30">|</span>
                        <span>EN</span>
                    </>
                )}
            </span>
        </button>
    );
}

export default LanguageSelector;
