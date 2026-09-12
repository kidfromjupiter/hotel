import Link from 'next/link';
import { HiChevronLeft } from 'react-icons/hi';
import BranchCard from '@/components/BranchCard';

const BRANCHES = [
  {
    id: 'colombo',
    name: 'SkyNest Colombo',
    city: 'Colombo',
    description:
      "Located in the heart of Sri Lanka's vibrant capital, SkyNest Colombo offers stunning urban skyline views, rooftop dining, an infinity pool, and seamless access to Colombo's finest attractions and business districts.",
    image: 'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&q=80',
    address: 'Colombo 03, Western Province, Sri Lanka',
  },
  {
    id: 'kandy',
    name: 'SkyNest Kandy',
    city: 'Kandy',
    description:
      "Nestled in the scenic hills of Sri Lanka's Cultural Capital, SkyNest Kandy blends colonial charm with modern luxury. Enjoy breathtaking views over Kandy Lake and easy access to the Temple of the Tooth.",
    image: 'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80',
    address: 'Kandy, Central Province, Sri Lanka',
  },
  {
    id: 'galle',
    name: 'SkyNest Galle',
    city: 'Galle',
    description:
      "Set within the shadow of the iconic Galle Fort, SkyNest Galle pairs Dutch colonial architecture with contemporary luxury. Wake up to Indian Ocean breezes and explore the historic fort steps from your door.",
    image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80',
    address: 'Galle Fort, Southern Province, Sri Lanka',
  },
];

export default function BranchSelectionPage() {
  return (
    <div className="min-h-screen bg-skynest-blue-pale pt-16">

      {/* ── Header ── */}
      <div className="bg-skynest-navy text-white py-12 px-4 shadow-lg">
        <div className="max-w-6xl mx-auto">
          <Link
            href="/"
            className="inline-flex items-center gap-0.5 text-skynest-blue-light text-xs hover:text-white transition-colors font-semibold tracking-wide mb-4"
          >
            <HiChevronLeft size={16} /> Back to Home
          </Link>
          <h1 className="text-3xl sm:text-4xl font-black text-white leading-tight">
            Select Your Branch
          </h1>
          <p className="text-gray-400 text-sm mt-2 max-w-xl leading-relaxed">
            Choose from our three stunning SkyNest locations across Sri Lanka to begin
            your booking. Each property offers a unique experience.
          </p>
        </div>
      </div>

      {/* ── Branch cards ── */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {BRANCHES.map(branch => (
            <BranchCard key={branch.id} {...branch} />
          ))}
        </div>

        {/* Membership teaser */}
        <div className="mt-12 flex items-start gap-4 px-6 py-5 bg-skynest-navy rounded-2xl shadow-lg">
          <span className="text-3xl flex-shrink-0">⭐</span>
          <div>
            <h3 className="text-white font-bold text-sm">SkyNest Membership</h3>
            <p className="text-gray-400 text-xs leading-relaxed mt-1">
              Already a SkyNest member? Enter your registered phone number during booking
              and exclusive member discounts will be automatically applied to all room rates.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
