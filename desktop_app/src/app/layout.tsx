import type { Metadata } from 'next'
import '../../styles/globals.css'

export const metadata: Metadata = {
  title: 'Quant AI Lab',
  description: 'AI-powered autonomous trading platform for Indian markets',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0a0a0f] text-slate-100 font-sans">
        {children}
      </body>
    </html>
  )
}
