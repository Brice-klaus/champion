tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        champion: {
          50:  '#FBEEEC',
          100: '#F5D9D4',
          200: '#E9B3AA',
          300: '#DB8D80',
          400: '#CB6B5C',
          500: '#C1503F',
          600: '#A83F30',
          700: '#873326',
          800: '#65261C',
          900: '#361611',
        },
        mangue: {
          100: '#FFF3C4',
          300: '#FFE175',
          500: '#FFD400',
          600: '#E0B300',
          700: '#A88600',
        },
        hibiscus: {
          300: '#FBBF88',
          500: '#E88A4A',
          600: '#C86F35',
        },
        creme: {
          50: '#FBF8F3',
          70: '#FFFFFF',
          100: '#F4EFE6',
        },
        nuit: {
          50:  '#EEF1F7',
          300: '#7C8CAE',
          400: '#4C5C82',
          500: '#2A3B5C',
          600: '#1C2842',
          700: '#141D33',
          800: '#0F1626',
          900: '#0A0F1C',
        },
      },
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        xl2: '1.5rem',
        xl3: '2rem',
      },
      boxShadow: {
        soft: '0 8px 30px -8px rgba(54, 22, 17, 0.16)',
        softdark: '0 8px 30px -8px rgba(0, 0, 0, 0.6)',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: 0, transform: 'translateY(24px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        floaty: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        marquee: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
      },
      animation: {
        fadeUp: 'fadeUp 0.7s cubic-bezier(0.16,1,0.3,1) both',
        floaty: 'floaty 6s ease-in-out infinite',
        marquee: 'marquee 28s linear infinite',
      },
    },
  },
};