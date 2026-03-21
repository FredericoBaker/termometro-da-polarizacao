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
        polarization: {
          low: '#3b82f6',
          mid: '#eab308',
          high: '#ef4444',
        },
        agreement: '#16a34a',
        disagreement: '#dc2626',
      },
    },
  },
  plugins: [typography],
}

export default config
