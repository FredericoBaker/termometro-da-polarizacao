import type { Config } from 'tailwindcss'
import typography from '@tailwindcss/typography'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        canvas: '#f6f6f3',
        ink: '#111827',
        brand: {
          50: '#eef1f5',
          100: '#d9e0ea',
          700: '#1f3149',
          800: '#17263a',
          900: '#111b2a',
        },
        polarization: {
          low: '#3a64a8',
          mid: '#c88b1f',
          high: '#a73737',
        },
        agreement: '#1f7a4f',
        disagreement: '#b24040',
      },
      fontFamily: {
        serif: ['var(--font-serif)', 'Georgia', 'serif'],
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [typography],
}

export default config
