'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getCurrentStaff } from '@/lib/api';

interface StaffRouteGuardProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'receptionist';
}

export default function StaffRouteGuard({ children, requiredRole }: StaffRouteGuardProps) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    let active = true;

    getCurrentStaff()
      .then((user) => {
        if (!active) return;
        if (requiredRole && user.role !== requiredRole) {
          router.replace(user.role === 'admin' ? '/admin' : '/receptionist');
          return;
        }
        setAuthorized(true);
      })
      .catch(() => {
        localStorage.removeItem('staff_token');
        localStorage.removeItem('staff_user');
        router.replace('/staff/login');
      });

    return () => {
      active = false;
    };
  }, [requiredRole, router]);

  if (!authorized) {
    return (
      <div className="min-h-screen bg-skynest-navy flex items-center justify-center text-white">
        Verifying staff access…
      </div>
    );
  }

  return children;
}
