"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { signIn } from "next-auth/react";

/* ------------------------------------------------------------------ */
/*  Animated counter hook                                              */
/* ------------------------------------------------------------------ */
function useCounter(target: number, duration: number = 2400) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true;
          const start = performance.now();
          const tick = (now: number) => {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // Ease-out cubic for that accelerating feel
            const eased = 1 - Math.pow(1 - progress, 3);
            setCount(Math.floor(eased * target));
            if (progress < 1) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        }
      },
      { threshold: 0.3 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [target, duration]);

  return { count, ref };
}

/* ------------------------------------------------------------------ */
/*  FAQ item                                                           */
/* ------------------------------------------------------------------ */
function FAQ({
  q,
  a,
  open,
  onClick,
}: {
  q: string;
  a: string;
  open: boolean;
  onClick: () => void;
}) {
  return (
    <div className="border-b border-white/10">
      <button
        onClick={onClick}
        className="w-full flex justify-between items-center py-5 text-left group cursor-pointer"
      >
        <span className="text-lg font-medium text-white/90 group-hover:text-white transition-colors">
          {q}
        </span>
        <span
          className={`text-2xl text-red-500 transition-transform duration-300 ${
            open ? "rotate-45" : ""
          }`}
        >
          +
        </span>
      </button>
      <div
        className={`overflow-hidden transition-all duration-300 ${
          open ? "max-h-40 pb-5" : "max-h-0"
        }`}
      >
        <p className="text-white/50 leading-relaxed">{a}</p>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Preset card                                                        */
/* ------------------------------------------------------------------ */
const presets = [
  {
    name: "Default",
    desc: "6 months old, preserve attachments",
    age: "180d",
    icon: "🎯",
  },
  {
    name: "Newsletters",
    desc: "Marketing emails & digests",
    age: "30d",
    icon: "📰",
  },
  {
    name: "GitHub",
    desc: "CI notifications & PR alerts",
    age: "7d",
    icon: "💻",
  },
  {
    name: "Large Emails",
    desc: "10MB+ storage hogs",
    age: "90d",
    icon: "📦",
  },
  {
    name: "Social Media",
    desc: "FB, Twitter, LinkedIn, Instagram",
    age: "14d",
    icon: "📱",
  },
  {
    name: "Promotional",
    desc: "Sales, discounts, deals",
    age: "60d",
    icon: "🛍️",
  },
];

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */
export default function LandingPage() {
  const hero = useCounter(17522, 2800);
  const speed = useCounter(83, 1600);
  const [faqOpen, setFaqOpen] = useState<number | null>(null);

  const faqs = [
    {
      q: "Is it safe? Will I lose important emails?",
      a: "Yes. We never touch emails marked important, starred, or with attachments. Everything is moved to trash first (recoverable for 30 days). You can preview exactly what will be deleted before running.",
    },
    {
      q: "Can I recover deleted emails?",
      a: "Emails are moved to Gmail's trash, where they stay for 30 days. You can recover anything from trash during that period.",
    },
    {
      q: "Do you store my email content?",
      a: "Never. We only access email metadata (sender, date, labels) to build the deletion query. Zero email content is ever stored on our servers.",
    },
    {
      q: "How is it so fast?",
      a: "Async batch processing with Gmail's Batch API. 5 concurrent workers, 300 emails per chunk, automatic rate limiting with exponential backoff. The engine was built for speed from day one.",
    },
    {
      q: "What happens if I hit a rate limit?",
      a: "The engine handles it automatically. It backs off, waits, and retries. You'll see a brief slowdown but it never crashes or loses progress.",
    },
  ];

  return (
    <div className="relative overflow-hidden">
      {/* Grid overlay */}
      <div
        className="pointer-events-none fixed inset-0 z-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,46,46,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,46,46,0.03) 1px, transparent 1px)
          `,
          backgroundSize: "60px 60px",
        }}
      />

      {/* Radial glow behind hero */}
      <div className="pointer-events-none absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full bg-red-600/10 blur-[120px] z-0" />

      {/* ============================================================ */}
      {/*  NAV                                                         */}
      {/* ============================================================ */}
      <nav className="relative z-10 flex items-center justify-between px-6 md:px-12 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <span className="text-2xl">☢️</span>
          <span className="font-[family-name:var(--font-jetbrains)] text-xl font-bold tracking-tight">
            MAIL<span className="text-red-500">NUKE</span>
          </span>
        </div>
        <div className="flex items-center gap-6">
          <a
            href="#pricing"
            className="text-sm text-white/50 hover:text-white transition-colors hidden sm:block"
          >
            Pricing
          </a>
          <a
            href="#faq"
            className="text-sm text-white/50 hover:text-white transition-colors hidden sm:block"
          >
            FAQ
          </a>
          <button
            onClick={() => signIn("google", { callbackUrl: "/dashboard" })}
            className="text-sm px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-all cursor-pointer"
          >
            Sign In
          </button>
        </div>
      </nav>

      {/* ============================================================ */}
      {/*  HERO                                                        */}
      {/* ============================================================ */}
      <section className="relative z-10 flex flex-col items-center text-center px-6 pt-20 pb-32 max-w-5xl mx-auto">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-[family-name:var(--font-jetbrains)] mb-8 animate-pulse">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
          SYSTEMS ONLINE
        </div>

        <h1 className="text-5xl sm:text-7xl md:text-8xl font-bold tracking-tight leading-none mb-6">
          Nuke your
          <br />
          <span className="bg-gradient-to-r from-red-500 via-orange-500 to-amber-500 bg-clip-text text-transparent">
            inbox
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-white/40 max-w-xl mb-12 leading-relaxed">
          Delete thousands of unwanted emails in seconds.
          <br className="hidden sm:block" />
          Smart filters protect what matters. Async engine does the rest.
        </p>

        {/* Counter */}
        <div ref={hero.ref} className="mb-12">
          <div className="font-[family-name:var(--font-jetbrains)] text-6xl sm:text-8xl font-bold tabular-nums tracking-tighter">
            <span className="bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent">
              {hero.count.toLocaleString()}
            </span>
          </div>
          <p className="text-white/30 text-sm font-[family-name:var(--font-jetbrains)] mt-2">
            EMAILS ELIMINATED
          </p>
        </div>

        {/* CTA */}
        <button
          onClick={() => signIn("google", { callbackUrl: "/dashboard" })}
          className="group relative inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-red-600 to-orange-600 rounded-xl text-lg font-semibold transition-all duration-300 hover:scale-105 hover:shadow-[0_0_40px_rgba(255,46,46,0.3)] cursor-pointer"
        >
          <span>Nuke My Inbox</span>
          <span className="text-xl group-hover:translate-x-1 transition-transform">
            →
          </span>
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-red-600 to-orange-600 opacity-0 group-hover:opacity-20 blur-xl transition-opacity" />
        </button>

        <p className="text-white/20 text-xs mt-4">
          Free tier available. No credit card required.
        </p>
      </section>

      {/* ============================================================ */}
      {/*  SPEED STAT                                                  */}
      {/* ============================================================ */}
      <section className="relative z-10 border-y border-white/5 bg-white/[0.02]">
        <div className="max-w-5xl mx-auto px-6 py-16 flex flex-col sm:flex-row items-center justify-center gap-12 sm:gap-24">
          <div ref={speed.ref} className="text-center">
            <div className="font-[family-name:var(--font-jetbrains)] text-5xl font-bold text-red-500 tabular-nums">
              {speed.count}
            </div>
            <p className="text-white/30 text-sm mt-1">emails / second</p>
          </div>
          <div className="text-center">
            <div className="font-[family-name:var(--font-jetbrains)] text-5xl font-bold text-white/20">
              ~2
            </div>
            <p className="text-white/30 text-sm mt-1">competitors avg</p>
          </div>
          <div className="text-center">
            <div className="font-[family-name:var(--font-jetbrains)] text-5xl font-bold text-green-500">
              40x
            </div>
            <p className="text-white/30 text-sm mt-1">faster</p>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  HOW IT WORKS                                                */}
      {/* ============================================================ */}
      <section className="relative z-10 max-w-5xl mx-auto px-6 py-24">
        <h2 className="text-3xl sm:text-4xl font-bold text-center mb-16">
          Three steps to{" "}
          <span className="text-red-500">zero inbox</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {[
            {
              step: "01",
              title: "Sign in with Google",
              desc: "One click. We request only the permissions needed to move emails to trash.",
            },
            {
              step: "02",
              title: "Pick a preset",
              desc: "Choose from 6 smart filters or build your own. Preview before you commit.",
            },
            {
              step: "03",
              title: "Watch them vanish",
              desc: "Live progress. Real-time speed counter. Thousands gone in seconds.",
            },
          ].map((item) => (
            <div
              key={item.step}
              className="group relative p-6 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] hover:border-red-500/20 transition-all duration-300"
            >
              <div className="font-[family-name:var(--font-jetbrains)] text-red-500/40 text-sm mb-4">
                {item.step}
              </div>
              <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
              <p className="text-white/40 text-sm leading-relaxed">
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ============================================================ */}
      {/*  PRESETS                                                     */}
      {/* ============================================================ */}
      <section className="relative z-10 max-w-5xl mx-auto px-6 pb-24">
        <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">
          Smart presets
        </h2>
        <p className="text-white/40 text-center mb-12 max-w-lg mx-auto">
          One click cleanup for the most common inbox polluters. Or build
          your own custom filter.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          {presets.map((p) => (
            <div
              key={p.name}
              className="group p-5 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] hover:border-white/10 transition-all"
            >
              <div className="text-2xl mb-3">{p.icon}</div>
              <h3 className="font-semibold text-sm mb-1">{p.name}</h3>
              <p className="text-white/30 text-xs mb-3">{p.desc}</p>
              <div className="font-[family-name:var(--font-jetbrains)] text-xs text-red-500/60">
                older_than: {p.age}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ============================================================ */}
      {/*  PRICING                                                     */}
      {/* ============================================================ */}
      <section
        id="pricing"
        className="relative z-10 max-w-5xl mx-auto px-6 pb-24"
      >
        <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">
          Pricing
        </h2>
        <p className="text-white/40 text-center mb-12">
          Start free. Upgrade when you need more firepower.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-3xl mx-auto">
          {/* Free */}
          <div className="p-8 rounded-xl border border-white/5 bg-white/[0.02]">
            <h3 className="text-lg font-semibold mb-1">Free</h3>
            <div className="font-[family-name:var(--font-jetbrains)] text-3xl font-bold mb-6">
              $0
            </div>
            <ul className="space-y-3 text-sm text-white/50 mb-8">
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> 1 cleanup / month
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> 500 emails max per
                run
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Default preset
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Dry run preview
              </li>
              <li className="flex items-center gap-2">
                <span className="text-white/20">—</span>{" "}
                <span className="text-white/20">Custom filters</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-white/20">—</span>{" "}
                <span className="text-white/20">Scheduled cleanup</span>
              </li>
            </ul>
            <Link
              href="/dashboard"
              className="block w-full text-center py-3 rounded-lg border border-white/10 text-sm hover:bg-white/5 transition-colors"
            >
              Get Started
            </Link>
          </div>

          {/* Pro */}
          <div className="relative p-8 rounded-xl border border-red-500/30 bg-gradient-to-b from-red-500/5 to-transparent">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-red-500 text-xs font-semibold rounded-full">
              POPULAR
            </div>
            <h3 className="text-lg font-semibold mb-1">Pro</h3>
            <div className="font-[family-name:var(--font-jetbrains)] text-3xl font-bold mb-1">
              $5
              <span className="text-base font-normal text-white/40">/mo</span>
            </div>
            <p className="text-xs text-white/30 mb-6">or $48/year (save 20%)</p>
            <ul className="space-y-3 text-sm text-white/50 mb-8">
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Unlimited cleanups
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Unlimited emails per
                run
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> All 6 presets +
                custom
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Dry run preview
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Inbox analytics
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Scheduled cleanup
              </li>
            </ul>
            <Link
              href="/dashboard"
              className="block w-full text-center py-3 rounded-lg bg-gradient-to-r from-red-600 to-orange-600 text-sm font-semibold hover:opacity-90 transition-opacity"
            >
              Upgrade to Pro
            </Link>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  FAQ                                                         */}
      {/* ============================================================ */}
      <section
        id="faq"
        className="relative z-10 max-w-3xl mx-auto px-6 pb-24"
      >
        <h2 className="text-3xl sm:text-4xl font-bold text-center mb-12">
          Questions
        </h2>
        <div>
          {faqs.map((faq, i) => (
            <FAQ
              key={i}
              q={faq.q}
              a={faq.a}
              open={faqOpen === i}
              onClick={() => setFaqOpen(faqOpen === i ? null : i)}
            />
          ))}
        </div>
      </section>

      {/* ============================================================ */}
      {/*  FOOTER                                                      */}
      {/* ============================================================ */}
      <footer className="relative z-10 border-t border-white/5">
        <div className="max-w-5xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-white/30 text-sm">
            <span>☢️</span>
            <span className="font-[family-name:var(--font-jetbrains)]">
              MAILNUKE
            </span>
            <span>· 2026</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-white/30">
            <a href="#" className="hover:text-white/60 transition-colors">
              Privacy
            </a>
            <a href="#" className="hover:text-white/60 transition-colors">
              Terms
            </a>
            <a
              href="https://github.com/adrozdenko/mailnuke"
              className="hover:text-white/60 transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
