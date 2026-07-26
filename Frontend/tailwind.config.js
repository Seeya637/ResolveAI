/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
        },
        accent: {
          100: '#EDE9FE',
          200: '#DDD6FE',
          400: '#A78BFA',
          500: '#8B5CF6',
          600: '#7C3AED',
        },
        blush: {
          100: '#FCE7F3',
          200: '#FBCFE8',
          400: '#F0ABDD',
        },
        success: {
          50: '#F0FDF4',
          100: '#DCFCE7',
          500: '#22C55E',
          600: '#16A34A',
          700: '#15803D',
        },
        ink: {
          900: '#0F172A',
          700: '#334155',
          500: '#64748B',
          300: '#CBD5E1',
          200: '#E2E8F0',
          100: '#F1F5F9',
          50: '#F8FAFC',
        },
        night: {
          950: '#0B0F1F',
          900: '#12172B',
          800: '#1A2036',
          700: '#242B45',
          500: '#5B6482',
          300: '#8B93B0',
        },
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(15, 23, 42, 0.04), 0 4px 16px rgba(15, 23, 42, 0.06)',
        'card-hover': '0 2px 4px rgba(15, 23, 42, 0.06), 0 8px 24px rgba(15, 23, 42, 0.10)',
        pop: '0 8px 30px rgba(37, 99, 235, 0.15)',
        glass: '0 8px 32px rgba(99, 102, 241, 0.10), 0 1px 2px rgba(15, 23, 42, 0.04)',
        'glass-dark': '0 8px 32px rgba(0, 0, 0, 0.35), 0 1px 2px rgba(0, 0, 0, 0.2)',
        'glow-primary': '0 8px 24px rgba(37, 99, 235, 0.35)',
      },
      backdropBlur: {
        xs: '2px',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: 0, transform: 'translateY(8px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        popIn: {
          '0%': { opacity: 0, transform: 'scale(0.85)' },
          '100%': { opacity: 1, transform: 'scale(1)' },
        },
        drawCheck: {
          '0%': { strokeDashoffset: 24 },
          '100%': { strokeDashoffset: 0 },
        },
        pulseRing: {
          '0%': { transform: 'scale(0.9)', opacity: 0.6 },
          '100%': { transform: 'scale(1.6)', opacity: 0 },
        },
      },
      animation: {
        fadeUp: 'fadeUp 0.45s ease-out both',
        fadeIn: 'fadeIn 0.4s ease-out both',
        popIn: 'popIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both',
        drawCheck: 'drawCheck 0.5s ease-out 0.2s both',
        pulseRing: 'pulseRing 1.8s cubic-bezier(0,0,0.2,1) infinite',
      },
    },
  },
  plugins: [],
}
