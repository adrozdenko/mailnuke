"use client";

import { useEffect, useState } from "react";
import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";

interface Preset {
  id: string;
  name: string;
  description: string;
  filters: Record<string, any>;
}

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export default function Dashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [presets, setPresets] = useState<Preset[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [preview, setPreview] = useState<{
    estimated_count: number;
    query: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [nuking, setNuking] = useState(false);
  const [progress, setProgress] = useState<{
    total_deleted: number;
    rate: number;
    progress_pct: number;
  } | null>(null);
  const [result, setResult] = useState<Record<string, any> | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (status === "unauthenticated") router.push("/");
  }, [status, router]);

  // Fetch presets
  useEffect(() => {
    fetch(`${API}/api/presets`)
      .then((r) => r.json())
      .then((d) => {
        setPresets(d.presets);
        if (d.presets.length > 0) setSelected(d.presets[0].id);
      })
      .catch(console.error);
  }, []);

  const selectedPreset = presets.find((p) => p.id === selected);

  // Preview
  async function handlePreview() {
    if (!selectedPreset) return;
    setLoading(true);
    setPreview(null);
    setResult(null);
    try {
      const res = await fetch(`${API}/api/cleanup/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(selectedPreset.filters),
      });
      const data = await res.json();
      setPreview(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  // Nuke
  function handleNuke() {
    if (!selectedPreset) return;
    setNuking(true);
    setResult(null);
    setProgress(null);

    const wsUrl = API.replace("http", "ws") + "/api/cleanup/run";
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      ws.send(JSON.stringify({ filters: selectedPreset.filters }));
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "progress") {
        setProgress({
          total_deleted: msg.total_deleted,
          rate: msg.rate,
          progress_pct: msg.progress_pct,
        });
      } else if (msg.type === "complete") {
        setResult(msg);
        setNuking(false);
        setProgress(null);
        ws.close();
      } else if (msg.type === "error") {
        console.error(msg.message);
        setNuking(false);
        ws.close();
      }
    };

    ws.onerror = () => {
      setNuking(false);
    };
  }

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="font-[family-name:var(--font-jetbrains)] text-white/30 animate-pulse">
          LOADING...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 md:px-12 py-4 border-b border-white/5">
        <div className="flex items-center gap-2">
          <span className="text-xl">☢️</span>
          <span className="font-[family-name:var(--font-jetbrains)] text-lg font-bold">
            MAIL<span className="text-red-500">NUKE</span>
          </span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-white/40">{session?.user?.email}</span>
          <button
            onClick={() => signOut({ callbackUrl: "/" })}
            className="text-sm text-white/30 hover:text-white/60 transition-colors cursor-pointer"
          >
            Sign out
          </button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-8">
        {/* Sidebar — Presets */}
        <div>
          <h2 className="text-xs font-[family-name:var(--font-jetbrains)] text-white/30 uppercase tracking-wider mb-4">
            Presets
          </h2>
          <div className="space-y-2">
            {presets.map((p) => (
              <button
                key={p.id}
                onClick={() => {
                  setSelected(p.id);
                  setPreview(null);
                  setResult(null);
                }}
                className={`w-full text-left p-3 rounded-lg border transition-all cursor-pointer ${
                  selected === p.id
                    ? "border-red-500/40 bg-red-500/5"
                    : "border-white/5 bg-white/[0.02] hover:bg-white/[0.04]"
                }`}
              >
                <div className="text-sm font-medium">{p.name}</div>
                <div className="text-xs text-white/30 mt-0.5">
                  {p.description}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Main content */}
        <div className="space-y-6">
          {/* Selected preset info */}
          {selectedPreset && (
            <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
              <h3 className="text-lg font-semibold mb-1">
                {selectedPreset.name}
              </h3>
              <p className="text-sm text-white/40 mb-4">
                {selectedPreset.description}
              </p>

              <div className="flex gap-3">
                <button
                  onClick={handlePreview}
                  disabled={loading || nuking}
                  className="px-4 py-2 text-sm border border-white/10 rounded-lg hover:bg-white/5 transition-colors disabled:opacity-30 cursor-pointer"
                >
                  {loading ? "Scanning..." : "Preview"}
                </button>

                {preview && !nuking && (
                  <button
                    onClick={handleNuke}
                    className="px-6 py-2 text-sm font-semibold bg-gradient-to-r from-red-600 to-orange-600 rounded-lg hover:opacity-90 transition-opacity cursor-pointer"
                  >
                    Nuke {preview.estimated_count.toLocaleString()} emails
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Preview result */}
          {preview && !nuking && !result && (
            <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
              <div className="flex items-baseline gap-3 mb-2">
                <span className="font-[family-name:var(--font-jetbrains)] text-3xl font-bold text-red-500">
                  {preview.estimated_count.toLocaleString()}
                </span>
                <span className="text-white/30 text-sm">
                  emails will be nuked
                </span>
              </div>
              <code className="text-xs text-white/20 block break-all">
                {preview.query}
              </code>
            </div>
          )}

          {/* Live progress */}
          {nuking && progress && (
            <div className="p-6 rounded-xl border border-red-500/20 bg-red-500/5">
              <div className="flex items-baseline gap-3 mb-4">
                <span className="font-[family-name:var(--font-jetbrains)] text-4xl font-bold text-red-500 tabular-nums">
                  {progress.total_deleted.toLocaleString()}
                </span>
                <span className="text-white/30 text-sm">deleted</span>
                <span className="ml-auto font-[family-name:var(--font-jetbrains)] text-sm text-orange-500">
                  {progress.rate} emails/sec
                </span>
              </div>
              <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-red-600 to-orange-600 rounded-full transition-all duration-300"
                  style={{ width: `${progress.progress_pct}%` }}
                />
              </div>
              <p className="text-xs text-white/20 mt-2 font-[family-name:var(--font-jetbrains)]">
                {progress.progress_pct}% complete
              </p>
            </div>
          )}

          {/* Completion result */}
          {result && (
            <div className="p-6 rounded-xl border border-green-500/20 bg-green-500/5">
              <h3 className="text-lg font-semibold text-green-400 mb-4">
                Nuke Complete
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div>
                  <div className="font-[family-name:var(--font-jetbrains)] text-2xl font-bold">
                    {result.total_deleted?.toLocaleString()}
                  </div>
                  <div className="text-xs text-white/30">deleted</div>
                </div>
                <div>
                  <div className="font-[family-name:var(--font-jetbrains)] text-2xl font-bold">
                    {result.total_errors || 0}
                  </div>
                  <div className="text-xs text-white/30">errors</div>
                </div>
                <div>
                  <div className="font-[family-name:var(--font-jetbrains)] text-2xl font-bold">
                    {result.duration_seconds?.toFixed(1)}s
                  </div>
                  <div className="text-xs text-white/30">duration</div>
                </div>
                <div>
                  <div className="font-[family-name:var(--font-jetbrains)] text-2xl font-bold">
                    {result.deletion_rate?.toFixed(0)}
                  </div>
                  <div className="text-xs text-white/30">emails/sec</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
