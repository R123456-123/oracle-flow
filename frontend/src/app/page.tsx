"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Activity,
  MapPin,
  Building,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";

export default function Home() {
  const [formData, setFormData] = useState({
    address: "123 Silicon Valley Blvd",
    property_type: "Commercial Tech Park",
    size_sqft: 25000,
    age_years: 3,
    has_legal_disputes: false,
  });

  const [status, setStatus] = useState<
    "idle" | "evaluating" | "complete" | "error"
  >("idle");
  const [result, setResult] = useState<any>(null);
  const [consoleLogs, setConsoleLogs] = useState<string[]>([]);

  // Simulates the AI Judge Console logs while waiting for the real API
  useEffect(() => {
    if (status === "evaluating") {
      setConsoleLogs(["[System] Initializing Multi-Agent System..."]);
      const logs = [
        "[Actor Agent] Analyzing empirical property data...",
        "[Actor Agent] Drafting baseline market valuation...",
        "[Actor Agent] Calculating liquidity indexes...",
        "[Judge Agent] Cross-referencing draft against safety parameters...",
        "[Judge Agent] Scanning for prompt injection vectors...",
        "[Judge Agent] Verifying lack of subjective bias...",
        "[System] Compiling strictly formatted JSON response...",
      ];

      let i = 0;
      const interval = setInterval(() => {
        if (i < logs.length) {
          setConsoleLogs((prev) => [...prev, logs[i]]);
          i++;
        }
      }, 800);
      return () => clearInterval(interval);
    }
  }, [status]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("evaluating");
    setResult(null);

    try {
      // Make sure your FastAPI backend is running!
      const API_BASE_URL =
        process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${API_BASE_URL}/api/v1/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) throw new Error("API failed");
      const data = await res.json();
      setResult(data);
      setStatus("complete");
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  return (
    <main className="min-h-screen p-6 md:p-12 flex flex-col xl:flex-row gap-8 items-start justify-center overflow-x-hidden">
      {/* LEFT SIDE: The Input Form */}
      <motion.div
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        className="glass-panel p-8 w-full xl:w-1/3 z-10"
      >
        <div className="flex items-center gap-3 mb-8">
          <Activity className="text-blue-500 w-8 h-8" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Oracle Flow
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div>
            <label className="text-sm text-slate-400 mb-1 flex items-center gap-2">
              <MapPin className="w-4 h-4" /> Address
            </label>
            <input
              type="text"
              className="w-full bg-slate-900/50 border border-slate-700 rounded-lg p-3 text-white outline-none focus:border-blue-500 transition-all"
              value={formData.address}
              onChange={(e) =>
                setFormData({ ...formData, address: e.target.value })
              }
              required
            />
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-1 flex items-center gap-2">
              <Building className="w-4 h-4" /> Property Type
            </label>
            <input
              type="text"
              className="w-full bg-slate-900/50 border border-slate-700 rounded-lg p-3 text-white outline-none focus:border-blue-500 transition-all"
              value={formData.property_type}
              onChange={(e) =>
                setFormData({ ...formData, property_type: e.target.value })
              }
              required
            />
          </div>

          <div className="flex gap-4">
            <div className="w-1/2">
              <label className="text-sm text-slate-400 mb-1 block">
                Size (SqFt)
              </label>
              <input
                type="number"
                className="w-full bg-slate-900/50 border border-slate-700 rounded-lg p-3 text-white outline-none focus:border-blue-500"
                value={formData.size_sqft}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    size_sqft: Number(e.target.value),
                  })
                }
                required
              />
            </div>
            <div className="w-1/2">
              <label className="text-sm text-slate-400 mb-1 block">
                Age (Years)
              </label>
              <input
                type="number"
                className="w-full bg-slate-900/50 border border-slate-700 rounded-lg p-3 text-white outline-none focus:border-blue-500"
                value={formData.age_years}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    age_years: Number(e.target.value),
                  })
                }
                required
              />
            </div>
          </div>

          <div className="flex items-center gap-3 mt-2">
            <input
              type="checkbox"
              id="legal"
              className="w-5 h-5 accent-purple-500"
              checked={formData.has_legal_disputes}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  has_legal_disputes: e.target.checked,
                })
              }
            />
            <label
              htmlFor="legal"
              className="text-sm text-slate-300 cursor-pointer"
            >
              Has known legal disputes?
            </label>
          </div>

          <button
            type="submit"
            disabled={status === "evaluating"}
            className="mt-6 w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-4 rounded-xl transition-all shadow-[0_0_20px_rgba(59,130,246,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {status === "evaluating" ? "Processing..." : "Generate Valuation"}
          </button>
        </form>
      </motion.div>

      {/* RIGHT SIDE: Dynamic Dashboard & AI Console */}
      <motion.div
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-full xl:w-2/3 flex flex-col gap-6"
      >
        {/* The AI Judge Console */}
        <div className="glass-panel p-6 font-mono text-sm h-64 overflow-y-auto flex flex-col justify-end">
          {status === "idle" && (
            <p className="text-slate-500">Waiting for input...</p>
          )}
          {consoleLogs.map((log, i) => (
            <motion.p
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={
                log?.includes("[System]")
                  ? "text-blue-400 mt-2"
                  : log?.includes("[Judge Agent]")
                    ? "text-purple-400"
                    : "text-green-400"
              }
            >
              {log}
            </motion.p>
          ))}
          {status === "error" && (
            <p className="text-red-500">Error: Could not connect to API.</p>
          )}
        </div>

        {/* The Animated Results Dashboard */}
        {status === "complete" && result && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-panel p-8"
          >
            <div className="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
              <h2 className="text-2xl font-bold text-white">
                Evaluation Results
              </h2>
              {result.is_safe_to_process ? (
                <span className="flex items-center gap-2 text-green-400 bg-green-400/10 px-4 py-2 rounded-full">
                  <ShieldCheck className="w-5 h-5" /> Safe
                </span>
              ) : (
                <span className="flex items-center gap-2 text-red-400 bg-red-400/10 px-4 py-2 rounded-full">
                  <AlertTriangle className="w-5 h-5" /> Rejected
                </span>
              )}
            </div>

            {result.is_safe_to_process ? (
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
                  <p className="text-slate-400 text-sm mb-2">
                    Estimated Market Value
                  </p>
                  <p className="text-3xl font-bold text-white">
                    ${result.market_value_range[0].toLocaleString()} - $
                    {result.market_value_range[1].toLocaleString()}
                  </p>
                </div>
                <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800">
                  <p className="text-slate-400 text-sm mb-2">
                    Liquidity (Resale Index)
                  </p>
                  <div className="flex items-center gap-4">
                    <div className="w-full bg-slate-700 h-3 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${result.resale_potential_index}%` }}
                        transition={{ duration: 1, delay: 0.5 }}
                        className="bg-blue-500 h-full"
                      />
                    </div>
                    <span className="text-xl font-bold">
                      {result.resale_potential_index}/100
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-red-950/30 border border-red-500/30 p-6 rounded-xl text-red-200">
                <h3 className="font-bold text-red-400 mb-2 text-lg">
                  Safety Violation Detected
                </h3>
                <p>{result.refusal_reason}</p>
              </div>
            )}
          </motion.div>
        )}
      </motion.div>
    </main>
  );
}
