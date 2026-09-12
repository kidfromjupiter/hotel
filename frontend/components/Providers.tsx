'use client';

import { Toaster } from 'react-hot-toast';

/**
 * Client-side providers wrapper.
 * Keeps the root layout a Server Component while hosting
 * client-only providers (toast notifications, future context, etc.)
 */
export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#0f172a',
            color: '#ffffff',
            border: '1px solid #1e293b',
            borderRadius: '12px',
            fontSize: '14px',
          },
          success: {
            style: {
              background: '#0f172a',
              color: '#bae6fd',
              border: '1px solid #0ea5e9',
            },
            iconTheme: {
              primary: '#0ea5e9',
              secondary: '#0f172a',
            },
          },
          error: {
            style: {
              background: '#0f172a',
              color: '#fca5a5',
              border: '1px solid #ef4444',
            },
          },
        }}
      />
    </>
  );
}
