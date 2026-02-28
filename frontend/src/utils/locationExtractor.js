/**
 * Location Extractor + OCR Processing Utility (v3 — Enhanced)
 * Handles:
 *  - Known Chennai area detection (English + Tamil + Tanglish)
 *  - Known landmark detection
 *  - Image preprocessing via Canvas API (grayscale, contrast, threshold)
 *  - OCR text cleaning (noise removal, common Tamil/English OCR error correction)
 *  - Fuzzy category matching (Levenshtein + keyword synonyms)
 * Pure client-side — no backend changes needed.
 */

// ─── Known Areas ───────────────────────────────────────────────────────────────
const KNOWN_AREAS = [
    { canonical: "Ambattur", variants: ["ambattur", "ambathur", "ambatur"] },
    { canonical: "Avadi", variants: ["avadi", "avadhi"] },
    { canonical: "Perambur", variants: ["perambur", "perampur", "peramboor", "peramber"] },
    { canonical: "Anna Nagar", variants: ["anna nagar", "annanagar", "anna nakar"] },
    { canonical: "Adyar", variants: ["adyar", "adiyar", "adayar"] },
    { canonical: "Velachery", variants: ["velachery", "velacheri", "velacherry", "velachary"] },
    { canonical: "T Nagar", variants: ["t nagar", "t.nagar", "tnagar", "thyagaraja nagar"] },
    { canonical: "Kodambakkam", variants: ["kodambakkam", "kodambakam", "kodambackam"] },
    { canonical: "Tambaram", variants: ["tambaram", "tamabaram", "thambaram"] },
    { canonical: "Chromepet", variants: ["chromepet", "chrompet", "chrome pet"] },
    { canonical: "Guindy", variants: ["guindy", "guindhy", "guindi"] },
    { canonical: "Mylapore", variants: ["mylapore", "mylappore", "mylapur"] },
    { canonical: "Nungambakkam", variants: ["nungambakkam", "nungambakam"] },
    { canonical: "Egmore", variants: ["egmore", "ezhmore", "ezhumbur"] },
    { canonical: "Royapettah", variants: ["royapettah", "royapetta", "royapettai"] },
    { canonical: "Kilpauk", variants: ["kilpauk", "kilpak", "kilpaak"] },
    { canonical: "Porur", variants: ["porur", "poroor"] },
    { canonical: "Vadapalani", variants: ["vadapalani", "vadapalni", "vadapazhani"] },
    { canonical: "Sholinganallur", variants: ["sholinganallur", "sholinganalloor", "shollinganallur"] },
    { canonical: "Pallikaranai", variants: ["pallikaranai", "pallikarnai"] },
    { canonical: "Medavakkam", variants: ["medavakkam", "medavakam", "medhavakkam"] },
    { canonical: "Thoraipakkam", variants: ["thoraipakkam", "thoraipakam"] },
    { canonical: "OMR", variants: ["omr", "old mahabalipuram road"] },
    { canonical: "ECR", variants: ["ecr", "east coast road"] },
    { canonical: "Mogappair", variants: ["mogappair", "mogapair", "mogapper"] },
    { canonical: "Kolathur", variants: ["kolathur", "kolattur"] },
    { canonical: "Villivakkam", variants: ["villivakkam", "villiwakkam", "villivakam"] },
    { canonical: "Madhavaram", variants: ["madhavaram", "madavaram", "madhavram"] },
    { canonical: "Tondiarpet", variants: ["tondiarpet", "tondiarpettai", "tondiyarpet"] },
    { canonical: "Washermanpet", variants: ["washermanpet", "washermenpet"] },
    { canonical: "Saidapet", variants: ["saidapet", "saidhapet", "saidapettai"] },
    { canonical: "Nandanam", variants: ["nandanam", "nandhnam"] },
    { canonical: "Ashok Nagar", variants: ["ashok nagar", "ashoknagar", "ashok nakar"] },
    { canonical: "KK Nagar", variants: ["kk nagar", "kknagar", "k.k.nagar"] },
    { canonical: "Thiruvanmiyur", variants: ["thiruvanmiyur", "thiruvanmyur", "thiruvanmiyoor"] },
    { canonical: "Besant Nagar", variants: ["besant nagar", "besantnagar", "elliot beach"] },
    { canonical: "Alwarpet", variants: ["alwarpet", "alwarpettai"] },
    { canonical: "Alandur", variants: ["alandur", "alandhur"] },
    { canonical: "Poonamallee", variants: ["poonamallee", "poonamalli", "poonamalee"] },
    { canonical: "Mangadu", variants: ["mangadu", "mangadhu"] },
];

// ─── Known Landmarks ──────────────────────────────────────────────────────────
const KNOWN_LANDMARKS = [
    { canonical: "Railway Station", variants: ["railway station", "train station", "rly station", "railway", "railwaystation", "station"] },
    { canonical: "Bus Stop", variants: ["bus stop", "bus stand", "bus depot", "bus terminus", "busstop", "bus station"] },
    { canonical: "Hospital", variants: ["hospital", "govt hospital", "government hospital", "dispensary", "medical"] },
    { canonical: "School", variants: ["school", "pallikoodam", "government school", "aided school"] },
    { canonical: "College", variants: ["college", "arts college", "engineering college"] },
    { canonical: "Temple", variants: ["temple", "kovil", "koil", "murugan kovil", "vinayagar kovil", "amman kovil"] },
    { canonical: "Church", variants: ["church", "chapel"] },
    { canonical: "Mosque", variants: ["mosque", "masjid", "dargah"] },
    { canonical: "Market", variants: ["market", "bazaar", "santhe", "weekly market", "supermarket", "super market"] },
    { canonical: "Park", variants: ["park", "garden", "playground", "ground"] },
    { canonical: "Police Station", variants: ["police station", "police", "kaval nilayam"] },
    { canonical: "Post Office", variants: ["post office", "postoffice"] },
    { canonical: "Bridge", variants: ["bridge", "palam", "flyover", "overbridge"] },
    { canonical: "Apartment", variants: ["apartment", "flats", "housing board", "tnhb"] },
];

// ─── Category Dictionary with Synonyms & Tanglish ────────────────────────────
const CATEGORY_KEYWORDS = {
    "Water Stagnation": [
        "water stagnation", "stagnation", "waterlogging", "flooding", "flood", "standing water",
        "thanni thengi", "thanni nikuthu", "thengi nikuthu", "thanni thangi", "thanni", "thengi",
        "water clogged", "water logged", "water block", "inundation", "ponding",
        "ooram thengi", "tannir thengi", "rain water", "rainwater stagnation",
    ],
    "Potholes": [
        "pothole", "potholes", "road damaged", "road damage", "crater", "road broken", "road crack",
        "road problem", "road issue", "road hole", "valithu", "paathai potholes", "vazhikadu",
        "broken road", "damaged road", "road bad", "uneven road", "road failure",
    ],
    "Garbage": [
        "garbage", "waste", "trash", "dump", "littering", "kupai", "kuppai", "dustbin",
        "solid waste", "junk", "litter", "debris", "refuse", "waste dumping", "illegal dumping",
        "garbage pile", "waste pile", "open garbage", "dirty", "unclean area",
    ],
    "Street Light": [
        "street light", "streetlight", "lamp post", "no light", "dark road", "lamp",
        "theru vilakku", "vilakku illai", "light illai", "no lighting", "street lamp",
        "road light", "power outage", "light out", "electrical issue road",
    ],
    "Public Toilet": [
        "toilet", "restroom", "public toilet", "sanitation", "lavatory", "bathroom",
        "open defecation", "urinal", "no toilet", "toilet broken", "dirty toilet",
    ],
    "Mosquito Menace": [
        "mosquito", "mosquitoes", "malaria", "dengue", "disease", "pest", "insect",
        "mosquito breeding", "stagnant water mosquito", "larvae", "breeding ground",
    ],
    "Storm Water Drain": [
        "storm water", "drain", "drainage", "blocked drain", "clogged drain", "sewage",
        "sewer", "drainage blocked", "kaluval", "water drain", "drain overflow",
        "choked drain", "gutter", "open drain", "nalah", "nala",
    ],
    "Stray Dogs": [
        "stray dog", "stray animal", "dog attack", "dog bite", "street dog",
        "rabies", "animal menace", "dog problem", "dog nuisance",
    ],
    "Fallen Tree": [
        "fallen tree", "tree fall", "tree fallen", "uprooted tree", "tree blocking",
        "tree on road", "branch fallen", "old tree", "dangerous tree", "tree damage",
    ],
    "Broken Garbage Bin": [
        "broken bin", "garbage bin", "broken garbage bin", "damaged dustbin",
        "dustbin broken", "bin missing", "no bin", "kuppai thotti", "thotti odaindha",
    ],
    "General": [
        "complaint", "problem", "issue", "civic", "report", "general", "other",
    ],
};

// ─── Common OCR Error Corrections ─────────────────────────────────────────────
const OCR_CORRECTIONS = {
    // Road / Infrastructure
    "pothoie": "pothole", "pothale": "pothole", "po1hole": "pothole",
    "rood": "road", "raod": "road",
    // Water
    "watcr": "water", "vvater": "water", "w4ter": "water",
    "stagnat1on": "stagnation", "stagnatlon": "stagnation", "stagnaton": "stagnation",
    "f1ood": "flood", "fiood": "flood",
    // Garbage
    "garbagc": "garbage", "garbaqe": "garbage",
    "trasb": "trash", "tra5h": "trash",
    // Drainage
    "dra1n": "drain", "drainaqe": "drainage", "dralnage": "drainage",
    // Street Light
    "llght": "light", "Iight": "light", "liqht": "light",
    // Railway
    "raliway": "railway", "railwav": "railway", "ralway": "railway",
    "statlon": "station", "stati0n": "station", "stasion": "station",
    // General
    "problern": "problem", "pr0blem": "problem",
    "compiaint": "complaint", "cornplaint": "complaint",
    "issiie": "issue", "lssue": "issue",
    // Tamil transliterations often split
    "tha nni": "thanni", "then gi": "thengi", "niku thu": "nikuthu",
    "peram bur": "perambur", "anna na gar": "anna nagar",
};

// ─── UTILITY: Levenshtein Distance ────────────────────────────────────────────
function levenshtein(a, b) {
    const m = a.length, n = b.length;
    const dp = Array.from({ length: m + 1 }, (_, i) => [i, ...Array(n).fill(0)]);
    for (let j = 0; j <= n; j++) dp[0][j] = j;
    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            dp[i][j] = a[i - 1] === b[j - 1]
                ? dp[i - 1][j - 1]
                : 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
        }
    }
    return dp[m][n];
}

/** Similarity ratio 0-1 between two strings */
function similarity(a, b) {
    if (!a || !b) return 0;
    const dist = levenshtein(a.toLowerCase(), b.toLowerCase());
    return 1 - dist / Math.max(a.length, b.length);
}

function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ─── 1. IMAGE PREPROCESSING (Canvas API) ───────────────────────────────────────
/**
 * Preprocess an image file for better OCR accuracy.
 * Applies: scale-up, grayscale, contrast boost, adaptive thresholding.
 * @param {File|Blob} imageFile
 * @returns {Promise<Blob>} preprocessed image blob
 */
export function preprocessImageForOCR(imageFile) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        const url = URL.createObjectURL(imageFile);

        img.onload = () => {
            // Scale: target 2400px on the longer side for OCR clarity
            const MAX = 2400;
            const scale = Math.min(MAX / Math.max(img.width, img.height), 3.0);
            const w = Math.round(img.width * scale);
            const h = Math.round(img.height * scale);

            const canvas = document.createElement('canvas');
            canvas.width = w;
            canvas.height = h;
            const ctx = canvas.getContext('2d');

            // White background (transparent PNGs cause OCR issues)
            ctx.fillStyle = '#FFFFFF';
            ctx.fillRect(0, 0, w, h);
            ctx.drawImage(img, 0, 0, w, h);
            URL.revokeObjectURL(url);

            const imageData = ctx.getImageData(0, 0, w, h);
            const d = imageData.data;

            // Pass 1: Convert to grayscale + boost contrast
            for (let i = 0; i < d.length; i += 4) {
                const gray = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
                // Contrast stretch: increase contrast by 1.6x around midpoint 128
                const c = Math.min(255, Math.max(0, (gray - 128) * 1.6 + 128));
                d[i] = d[i + 1] = d[i + 2] = c;
                d[i + 3] = 255;
            }

            // Pass 2: Adaptive-like threshold — pixels below 140 become black, above 140 become white
            for (let i = 0; i < d.length; i += 4) {
                const bw = d[i] < 140 ? 0 : 255;
                d[i] = d[i + 1] = d[i + 2] = bw;
            }

            ctx.putImageData(imageData, 0, 0);

            canvas.toBlob((blob) => {
                if (blob) resolve(blob);
                else reject(new Error('Canvas toBlob failed'));
            }, 'image/png');
        };

        img.onerror = () => reject(new Error('Image load failed'));
        img.src = url;
    });
}

// ─── 2. OCR TEXT CLEANING ──────────────────────────────────────────────────────
/**
 * Clean and normalize raw OCR output.
 * - Removes noise characters
 * - Fixes known OCR substitution errors
 * - Normalizes whitespace and line breaks
 * - Fixes broken/split Tamil transliterations
 * @param {string} rawText
 * @returns {string} cleaned text
 */
export function cleanOCRText(rawText) {
    if (!rawText) return '';

    let text = rawText;

    // 1. Replace line breaks / form-feeds with spaces
    text = text.replace(/[\r\n\f\t]+/g, ' ');

    // 2. Remove non-printable / weird unicode characters
    text = text.replace(/[^\x20-\x7E\u0B80-\u0BFF]/g, ' ');

    // 3. Remove sequences of special chars that are clearly noise
    text = text.replace(/[!@#$%^&*()_+=\[\]{};:"\\|<>?~`]{2,}/g, ' ');

    // 4. Remove isolated single special chars (except . , ' -)
    text = text.replace(/(?<![a-zA-Z])[^a-zA-Z0-9\s.,'\\-](?![a-zA-Z])/g, ' ');

    // 5. Fix known OCR word substitution errors
    for (const [wrong, right] of Object.entries(OCR_CORRECTIONS)) {
        const regex = new RegExp(`\\b${escapeRegex(wrong)}\\b`, 'gi');
        text = text.replace(regex, right);
    }

    // 6. Remove repeated characters (e.g., "sttttagnation" → "stagnation")
    text = text.replace(/(.)\1{3,}/g, '$1');

    // 7. Collapse multiple spaces
    text = text.replace(/\s+/g, ' ').trim();

    // 8. Capitalize first letter of each sentence
    text = text.replace(/(^\w|[.!?]\s+\w)/g, (c) => c.toUpperCase());

    return text;
}

// ─── 3. FUZZY CATEGORY MATCHING ───────────────────────────────────────────────
/**
 * Match cleaned text to a complaint category using:
 *  - Exact keyword search (phase 1)
 *  - Fuzzy Levenshtein similarity per word (phase 2 fallback)
 *  - Synonym / Tanglish matching
 * Returns the best matching category name, or "General" if nothing matches.
 * @param {string} text
 * @returns {{ category: string, confidence: number }}
 */
export function fuzzyMatchCategory(text) {
    if (!text) return { category: 'General', confidence: 0 };

    const lower = text.toLowerCase();
    const words = lower.split(/\s+/);
    const scores = {};

    for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
        let score = 0;

        for (const kw of keywords) {
            // Phase 1: exact substring match (high score)
            if (lower.includes(kw)) {
                score += 1.0 + kw.length * 0.02; // longer match = higher score
                continue;
            }

            // Phase 2: fuzzy match against individual words in text
            for (const word of words) {
                const sim = similarity(word, kw);
                if (sim >= 0.80) {
                    score += sim * 0.7;
                    break;
                }
            }

            // Phase 3: fuzzy match against multi-word keyword phrases
            if (kw.includes(' ')) {
                const kwWords = kw.split(' ');
                const sim = similarity(lower.slice(0, kw.length + 10), kw);
                if (sim >= 0.75) {
                    score += sim * 0.8;
                }
            }
        }

        scores[category] = score;
    }

    // Rank by score
    const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
    const [bestCat, bestScore] = sorted[0];

    // Minimum threshold: if best score is 0 or very low, return General
    if (bestScore < 0.3) return { category: 'General', confidence: 0.1 };

    const confidence = Math.min(0.99, bestScore / 3.0);
    return { category: bestCat, confidence };
}

// ─── 4. FULL OCR PIPELINE ─────────────────────────────────────────────────────
/**
 * Full OCR pipeline:
 * 1. Preprocess image (Canvas: grayscale + contrast + threshold)
 * 2. Run Tesseract OCR
 * 3. Clean extracted text
 * 4. Fuzzy-match category
 * 5. Extract location from cleaned text
 *
 * @param {File|Blob} imageFile
 * @param {Function} onProgress - receives 0-100
 * @returns {Promise<{ rawText, cleanedText, category, confidence, location }>}
 */
export async function runOCRPipeline(imageFile, onProgress) {
    // Step 1: Preprocess
    let processedFile = imageFile;
    try {
        const preprocessed = await preprocessImageForOCR(imageFile);
        processedFile = preprocessed;
    } catch (e) {
        console.warn('Preprocessing failed, using raw image:', e);
    }

    // Step 2: Tesseract OCR
    const { createWorker } = await import('tesseract.js');
    if (onProgress) onProgress(5);

    const worker = await createWorker('eng+tam', 1, {
        logger: (m) => {
            if (m.status === 'recognizing text' && onProgress) {
                onProgress(10 + Math.round(m.progress * 80));
            }
        },
    });

    const { data: { text: rawText } } = await worker.recognize(processedFile);
    await worker.terminate();
    if (onProgress) onProgress(95);

    // Step 3: Clean
    const cleanedText = cleanOCRText(rawText);

    // Step 4: Fuzzy category match
    const { category, confidence } = fuzzyMatchCategory(cleanedText);

    // Step 5: Location extract
    const location = extractLocationFromText(cleanedText);

    if (onProgress) onProgress(100);

    return { rawText, cleanedText, category, confidence, location };
}

// ─── 5. LOCATION EXTRACTION ───────────────────────────────────────────────────
/**
 * Extract area + landmark from any text (English, Tamil, Tanglish).
 */
export function extractLocationFromText(text) {
    if (!text || text.trim().length === 0) {
        return { areaName: null, landmark: null, confidence: 0, source: 'none' };
    }

    const lowerText = text.toLowerCase();
    let bestArea = null, bestAreaConf = 0;

    for (const area of KNOWN_AREAS) {
        for (const variant of area.variants) {
            const regex = new RegExp(
                `(?:^|[\\s,.(\\[{-])${escapeRegex(variant)}(?:[\\s,.)\\]}-]|la|le|il|ula|ku|kku|$)`, 'i'
            );
            if (regex.test(lowerText)) {
                const score = Math.min(0.95, 0.6 + variant.length / Math.max(lowerText.length, 1));
                if (score > bestAreaConf) { bestAreaConf = score; bestArea = area.canonical; }
            }
        }
    }

    // Fuzzy area fallback
    if (!bestArea) {
        for (const area of KNOWN_AREAS) {
            for (const variant of area.variants) {
                for (const word of lowerText.split(/\s+/)) {
                    if (word.length > 3 && similarity(word, variant) >= 0.82) {
                        bestArea = area.canonical;
                        bestAreaConf = 0.55;
                        break;
                    }
                }
                if (bestArea) break;
            }
            if (bestArea) break;
        }
    }

    let bestLandmark = null;
    for (const lm of KNOWN_LANDMARKS) {
        for (const variant of lm.variants) {
            if (lowerText.includes(variant)) { bestLandmark = lm.canonical; break; }
        }
        if (bestLandmark) break;
    }

    // Fuzzy landmark fallback
    if (!bestLandmark) {
        for (const lm of KNOWN_LANDMARKS) {
            for (const variant of lm.variants) {
                for (const word of lowerText.split(/\s+/)) {
                    if (word.length > 3 && similarity(word, variant) >= 0.80) {
                        bestLandmark = lm.canonical; break;
                    }
                }
                if (bestLandmark) break;
            }
            if (bestLandmark) break;
        }
    }

    return { areaName: bestArea, landmark: bestLandmark, confidence: bestAreaConf, source: 'text' };
}

// ─── 6. ZONE MAPPING ──────────────────────────────────────────────────────────
export function mapAreaToZone(areaName) {
    if (!areaName) return null;
    const ZONES = ["Ambattur", "Avadi", "Perambur", "Anna Nagar", "Adyar", "Velachery"];
    const lower = areaName.toLowerCase();

    const direct = ZONES.find(z => z.toLowerCase() === lower);
    if (direct) return direct;

    const ZONE_MAP = {
        "Ambattur": ["ambattur", "mogappair", "kolathur", "villivakkam", "madhavaram", "poonamallee", "mangadu"],
        "Avadi": ["avadi"],
        "Perambur": ["perambur", "tondiarpet", "washermanpet", "egmore", "kilpauk"],
        "Anna Nagar": ["anna nagar", "kk nagar", "ashok nagar", "vadapalani", "kodambakkam", "nungambakkam"],
        "Adyar": ["adyar", "thiruvanmiyur", "besant nagar", "alwarpet", "mylapore", "saidapet", "nandanam", "guindy", "alandur"],
        "Velachery": ["velachery", "pallikaranai", "medavakkam", "thoraipakkam", "sholinganallur", "chromepet", "tambaram", "omr", "ecr"],
    };

    for (const [zone, areas] of Object.entries(ZONE_MAP)) {
        if (areas.some(a => lower.includes(a) || a.includes(lower))) return zone;
    }
    return null;
}

// ─── 7. WEB SPEECH API ────────────────────────────────────────────────────────
export function transcribeWithSpeechAPI() {
    return new Promise((resolve, reject) => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) { reject(new Error('Speech recognition not supported.')); return; }
        const recognition = new SpeechRecognition();
        recognition.lang = 'ta-IN';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        recognition.onresult = (e) => resolve(e.results[0][0].transcript);
        recognition.onerror = (e) => reject(new Error(e.error));
        recognition.start();
    });
}

// ─── 8. LEGACY extractTextFromImage (kept for backward compat) ────────────────
export async function extractTextFromImage(imageFile, onProgress) {
    const result = await runOCRPipeline(imageFile, onProgress);
    return result.cleanedText;
}

// ─── 9. GREATER CHENNAI CORPORATION — 15 OFFICIAL ZONES ──────────────────────
/**
 * Full GCC zone-to-locality mapping.
 * Each zone key is the official zone name.
 * Localities are lowercase for matching against Nominatim address fields.
 */
export const GCC_ZONE_MAP = {
    "Thiruvottiyur Zone": [
        "thiruvottiyur", "kattivakkam", "kathivakkam", "ennore", "kaladipet",
        "surapet", "theradi", "thillaknagar", "new washermanpet", "tolgate"
    ],
    "Manali Zone": [
        "manali", "manali new town", "pattabiram", "minjur", "madhuravoyal"
    ],
    "Madhavaram Zone": [
        "madhavaram", "kolathur", "villivakkam", "periyar nagar", "kodungaiyur",
        "korukkupet", "mullai nagar", "sembium", "puzhal"
    ],
    "Tondiarpet Zone": [
        "tondiarpet", "tondiarpettai", "washermanpet", "royapuram",
        "harbour", "ayanavaram"
    ],
    "Royapuram Zone": [
        "royapuram", "george town", "georgetown", "park town", "sowcarpet",
        "mint", "big street", "mannady", "old washermanpet"
    ],
    "Thiru Vi Ka Nagar Zone": [
        "perambur", "purasaiwakkam", "purasawalkam", "egmore", "vepery",
        "kilpauk", "aminjikarai", "chetpet", "kotturpuram"
    ],
    "Ambattur Zone": [
        "ambattur", "padi", "mogappair", "nerkundram", "avadi",
        "korattur", "erukkancheri", "anna nagar west", "ambattur industrial estate"
    ],
    "Anna Nagar Zone": [
        "anna nagar", "annanagar", "kk nagar", "k.k.nagar", "ashok nagar",
        "arumbakkam", "shenoy nagar", "thirumangalam", "ayyapakkam"
    ],
    "Teynampet Zone": [
        "teynampet", "nungambakkam", "t nagar", "tnagar", "royapettah",
        "thousand lights", "alwarpet", "gopalapuram", "cenotaph road",
        "chamiers road", "egmore south"
    ],
    "Kodambakkam Zone": [
        "kodambakkam", "vadapalani", "virugambakkam", "koyambedu",
        "aminjikarai", "mahalingapuram", "choolaimedu", "saligramam"
    ],
    "Valasaravakkam Zone": [
        "valasaravakkam", "porur", "ramapuram", "mugalivakkam", "poonamallee",
        "mangadu", "alwar thirunagar", "alapakkam", "karambakkam"
    ],
    "Alandur Zone": [
        "alandur", "saidapet", "guindy", "st thomas mount", "saint thomas mount",
        "pallavaram", "chromepet", "chrompet", "nanganallur", "meenambakkam",
        "zamin pallavaram"
    ],
    "Adyar Zone": [
        "adyar", "besant nagar", "thiruvanmiyur", "mylapore", "nandanam",
        "kotturpuram", "foreshore estate", "lady andal", "valmiki nagar",
        "palavakkam", "sholinganallur south"
    ],
    "Perungudi Zone": [
        "perungudi", "medavakkam", "pallikaranai", "thoraipakkam",
        "karapakkam", "okkiyam thoraipakkam", "madipakkam", "jalladianpet",
        "perumbakkam"
    ],
    "Sholinganallur Zone": [
        "sholinganallur", "velachery", "taramani", "omr", "old mahabalipuram road",
        "ecr", "east coast road", "tambaram", "selaiyur", "chitlapakkam",
        "pammal", "kundrathur", "injambakkam", "kottivakkam", "uthandi"
    ]
};

/**
 * Detect official GCC zone from a raw address string (from Nominatim reverse geocode).
 * Checks suburb, neighbourhood, city_district, road, and full display name.
 * @param {Object} nominatimAddress - address object from Nominatim response
 * @returns {string|null} Official GCC zone name, or null if undetectable
 */
export function detectZoneFromAddress(nominatimAddress) {
    if (!nominatimAddress) return null;

    const addr = nominatimAddress;
    // Build a combined search string from all relevant Nominatim address fields
    const searchText = [
        addr.suburb, addr.neighbourhood, addr.quarter,
        addr.city_district, addr.county, addr.road,
        addr.pedestrian, addr.residential, addr.town,
        addr.village, addr.display_name
    ].filter(Boolean).join(' ').toLowerCase();

    // Score each zone by how many of its localities appear in the address
    const scores = {};
    for (const [zone, localities] of Object.entries(GCC_ZONE_MAP)) {
        let score = 0;
        for (const loc of localities) {
            if (searchText.includes(loc)) {
                // Longer match = more specific = higher confidence
                score += loc.split(' ').length * loc.length;
            }
        }
        scores[zone] = score;
    }

    const best = Object.entries(scores).sort((a, b) => b[1] - a[1])[0];
    return best && best[1] > 0 ? best[0] : null;
}

/**
 * Detect GCC zone from a plain area name string (for manual entry / text detection).
 * Uses exact + fuzzy substring matching against all locality lists.
 * @param {string} areaName
 * @returns {string|null} Official GCC zone name, or null
 */
export function detectZoneFromAreaName(areaName) {
    if (!areaName) return null;
    const lower = areaName.toLowerCase().trim();

    let bestZone = null;
    let bestLen = 0;

    for (const [zone, localities] of Object.entries(GCC_ZONE_MAP)) {
        for (const loc of localities) {
            // Exact or substring match
            if (lower.includes(loc) || loc.includes(lower)) {
                if (loc.length > bestLen) {
                    bestLen = loc.length;
                    bestZone = zone;
                }
            }
            // Fuzzy fallback for typos (Levenshtein)
            if (loc.length > 4 && similarity(lower, loc) >= 0.82) {
                if (loc.length > bestLen) {
                    bestLen = loc.length;
                    bestZone = zone;
                }
            }
        }
    }
    return bestZone;
}

/**
 * Forward geocode an area name to lat/lng using Nominatim (free, no API key).
 * Returns { lat, lng, address } or null.
 * @param {string} areaName
 * @returns {Promise<{lat: number, lng: number, address: Object}|null>}
 */
export async function forwardGeocode(areaName) {
    if (!areaName || areaName.trim().length < 2) return null;
    try {
        const query = encodeURIComponent(`${areaName}, Chennai, Tamil Nadu, India`);
        const res = await fetch(
            `https://nominatim.openstreetmap.org/search?q=${query}&format=json&addressdetails=1&limit=1`,
            { headers: { 'Accept-Language': 'en' } }
        );
        const data = await res.json();
        if (!data || data.length === 0) return null;
        return {
            lat: parseFloat(data[0].lat),
            lng: parseFloat(data[0].lon),
            address: data[0].address
        };
    } catch (err) {
        console.warn('Forward geocode failed:', err);
        return null;
    }
}

export default {
    extractLocationFromText, mapAreaToZone,
    transcribeWithSpeechAPI, extractTextFromImage,
    runOCRPipeline, cleanOCRText, preprocessImageForOCR, fuzzyMatchCategory,
    detectZoneFromAddress, detectZoneFromAreaName, forwardGeocode,
    GCC_ZONE_MAP
};
