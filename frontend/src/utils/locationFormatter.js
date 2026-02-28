/**
 * Location Formatter Utility
 * Handles parsing and robust display of civic location strings.
 * Fixes NaN display issues and float-formatted pincodes.
 */

/**
 * Parsed location object
 * @typedef {Object} LocationDetails
 * @property {string|null} lat
 * @property {string|null} lng
 * @property {string|null} address
 * @property {string|null} pincode
 * @property {boolean} isManual
 */

/**
 * Parses a hybrid location string (e.g. "lat, lng | address" or "Area, Landmark, PIN: 600011")
 * @param {string} locationStr 
 * @returns {LocationDetails}
 */
export function parseLocation(locationStr) {
    const details = {
        lat: null,
        lng: null,
        address: null,
        pincode: null,
        isManual: true
    };

    if (!locationStr) return details;

    // 1. Check for "|" delimiter (Map mode)
    if (locationStr.includes('|')) {
        const [coords, ...rest] = locationStr.split('|');
        const addr = rest.join('|').trim();
        details.address = addr;

        const coordParts = coords.split(',').map(s => s.trim());
        const lat = parseFloat(coordParts[0]);
        const lng = parseFloat(coordParts[1]);

        if (!isNaN(lat) && !isNaN(lng)) {
            details.lat = lat.toFixed(5);
            details.lng = lng.toFixed(5);
            details.isManual = false;
        }
    } else {
        // 2. Manual mode or Legacy string
        details.address = locationStr.trim();

        // Try to extract coordinates if they are hidden in the string (unlikely but safe)
        const coordMatches = locationStr.match(/(-?\d+\.\d+),\s*(-?\d+\.\d+)/);
        if (coordMatches) {
            const lat = parseFloat(coordMatches[1]);
            const lng = parseFloat(coordMatches[2]);
            if (!isNaN(lat) && !isNaN(lng)) {
                details.lat = lat.toFixed(5);
                details.lng = lng.toFixed(5);
                details.isManual = false;
            }
        }
    }

    // 3. Extract and Clean Pincode
    // Look for "PIN: 600011", "Pincode: 600011", or just a 6-digit number sequence
    const pinRegex = /(?:pin|pincode|postcode)[:\s]*(\d{6}(?:\.\d+)?)/i;
    const pinMatch = locationStr.match(pinRegex);
    if (pinMatch) {
        // Force to integer-like string to remove .00000
        const rawPin = pinMatch[1];
        details.pincode = Math.floor(parseFloat(rawPin)).toString();
    } else {
        // Fallback: look for any 6 digit number at the end or surrounded by non-digits
        const genericPinMatch = locationStr.match(/(?:\D|^)(\d{6})(?:\.0+)?(?:\D|$)/);
        if (genericPinMatch) {
            details.pincode = genericPinMatch[1];
        }
    }

    return details;
}

/**
 * Formats a location string for display in the UI.
 * @param {string} locationStr 
 * @returns {string}
 */
export function formatLocation(locationStr) {
    if (!locationStr) return "Location pending";

    const d = parseLocation(locationStr);

    if (d.lat && d.lng) {
        return `${d.lat}, ${d.lng}`;
    }

    if (d.address) {
        // For manual entries, show the first part of the address as the "location"
        const firstPart = d.address.split(',')[0].trim();
        return firstPart || "Manual Location";
    }

    return "Manual Location Provided";
}

/**
 * Returns a clean address display with pincode
 * @param {string} locationStr 
 * @returns {string}
 */
export function formatAddress(locationStr) {
    if (!locationStr) return "No specific address provided";

    const d = parseLocation(locationStr);

    // If it's just coordinates without an address, return a helpful msg or the coords
    if (!d.address) {
        if (d.lat && d.lng) return `Coordinates: ${d.lat}, ${d.lng}`;
        return "No specific address provided";
    }

    // Special case: if address is just "Manual" or similar, it's not very helpful
    if (d.address.toLowerCase().trim() === 'manual') {
        return "Manual address - details not specified";
    }

    // Clean decimals from pincode in the address string if it exists
    let cleanedAddress = d.address;
    if (d.pincode) {
        const floatPinRegex = new RegExp(`(${d.pincode})\\.\\d+`, 'g');
        cleanedAddress = cleanedAddress.replace(floatPinRegex, '$1');
    }

    return cleanedAddress;
}

/**
 * Formats a zone string consistently, ensuring "Zone" is appended exactly once.
 * Examples: "Tondiarpet" -> "Tondiarpet Zone", "Tondiarpet Zone" -> "Tondiarpet Zone"
 * @param {string} zoneStr 
 * @returns {string}
 */
export function formatZone(zoneStr) {
    if (!zoneStr) return "";
    let trimmed = zoneStr.trim();
    if (!trimmed) return "";

    // Case-insensitive check for "zone" at the end of the string
    const zoneRegex = /\s+zone$/i;
    if (zoneRegex.test(trimmed)) {
        // Normalize the capitalization
        trimmed = trimmed.replace(zoneRegex, ' Zone');
    } else {
        trimmed += ' Zone';
    }

    return trimmed;
}

export default {
    parseLocation,
    formatLocation,
    formatAddress,
    formatZone
};
