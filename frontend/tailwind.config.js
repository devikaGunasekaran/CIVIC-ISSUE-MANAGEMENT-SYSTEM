/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: "#5E7D32", // Conifer
                secondary: "#435929", // Meadow
                accent: "#E2EFDA", // Pistachio (Base background)
                highlight: "#92A64E", // Citron
                earth: "#717A44", // Moss
                warm: "#76632B", // Tortoise
                mint: "#E8F5E9", // SaaS Sidebar Mint
                white: "#FFFFFF",
                gray: {
                    900: "#1F2937", // Dark gray for text
                    800: "#374151",
                    700: "#4B5563",
                    600: "#6B7280",
                }
            },
            fontFamily: {
                sans: ['Inter', 'Poppins', 'sans-serif'],
            },
            borderRadius: {
                '2xl': '1rem',
                '3xl': '1.5rem',
            },
            boxShadow: {
                'soft': '0 4px 20px rgba(67, 89, 41, 0.05)',
                'premium': '0 10px 40px rgba(67, 89, 41, 0.08)',
            }
        },
    },
    plugins: [],
}
