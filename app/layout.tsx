import type { Metadata } from "next"
import { Playfair_Display, JetBrains_Mono } from "next/font/google"
import "./globals.css"

const playfair = Playfair_Display({ subsets: ["latin"], variable: "--font-playfair" })
const jetbrains = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" })

export const metadata: Metadata = {
  title: "Copilot Hub",
  description: "Custom AI agents for every task",
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className={`${playfair.variable} ${jetbrains.variable}`}>{children}</body>
    </html>
  )
}
