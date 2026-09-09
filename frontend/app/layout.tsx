import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Navbar from '@/components/Navbar';
import Providers from '@/components/Providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'SkyNest — Luxury Hotels in Sri Lanka',
  description:
    'Book your perfect stay at SkyNest Hotels — Colombo, Kandy, and Galle. Experience world-class luxury with warm Sri Lankan hospitality.',
  keywords: ['SkyNest', 'hotel', 'Sri Lanka', 'Colombo', 'Kandy', 'Galle', 'luxury', 'booking'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <Navbar />
          <main>{children}</main>
        </Providers>
      </body>
    </html>
  );
}
