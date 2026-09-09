import { notFound } from 'next/navigation';
import BookingWizard from '@/components/BookingWizard';

const VALID_BRANCHES = ['colombo', 'kandy', 'galle'] as const;
type ValidBranch = (typeof VALID_BRANCHES)[number];

interface PageProps {
  params: Promise<{ branch: string }>;
}

export default async function BranchBookingPage({ params }: PageProps) {
  const { branch: rawBranch } = await params;
  const branch = rawBranch.toLowerCase() as ValidBranch;

  if (!VALID_BRANCHES.includes(branch)) {
    notFound();
  }

  return <BookingWizard branch={branch} />;
}

/** Pre-render all three branch pages at build time */
export function generateStaticParams() {
  return VALID_BRANCHES.map(branch => ({ branch }));
}
