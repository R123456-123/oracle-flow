"use client";

import { useEffect, useState } from "react";
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ChevronDown,
  Clock3,
  Layers3,
  ScanSearch,
  ShieldCheck,
  Target,
  TrendingUp,
} from "lucide-react";

interface AuditLog {
  verified_drivers: string[];
  flagged_risks: string[];
  hallucination_check: string;
  prompt_injection_detected: boolean;
  bias_or_unsubstantiated_premium_flagged: boolean;
}

interface ValuationResult {
  is_safe_to_process: boolean;
  refusal_reason: string | null;
  market_value_range: number[];
  distress_value_range: number[];
  resale_potential_index: number;
  estimated_time_to_sell_days: number[];
  agent_confidence_score: number;
  oversight_audit_log: AuditLog;
}

type Status = "idle" | "evaluating" | "complete" | "error";

const steps = [
  ["01", "Research", "Normalize the property details and identify initial risk signals."],
  ["02", "Actor", "Draft an empirical valuation using the property characteristics."],
  ["03", "Judge", "Review the draft for safety, bias, and schema compliance."],
];

export default function Home() {
  const [formData, setFormData] = useState({
    address: "123 Silicon Valley Blvd",
    property_type: "Commercial Tech Park",
    size_sqft: 25000,
    age_years: 3,
    has_legal_disputes: false,
  });
  const [status, setStatus] = useState<Status>("idle");
  const [result, setResult] = useState<ValuationResult | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [auditExpanded, setAuditExpanded] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [activeStep, setActiveStep] = useState(-1);

  useEffect(() => {
    if (status !== "evaluating") return;
    const timer = window.setInterval(() => {
      setActiveStep((current) => Math.min(current + 1, 3));
    }, 1200);
    return () => window.clearInterval(timer);
  }, [status]);

  const updateField = (
    field: keyof typeof formData,
    value: string | number | boolean,
  ) => {
    setFormData((current) => ({ ...current, [field]: value }));
    setFormErrors((current) => ({ ...current, [field]: "" }));
  };

  const validate = () => {
    const errors: Record<string, string> = {};
    if (formData.address.trim().length < 3) errors.address = "Enter at least 3 characters.";
    if (formData.property_type.trim().length < 3) errors.property_type = "Enter a property type.";
    if (!formData.size_sqft || formData.size_sqft < 10) errors.size_sqft = "Minimum size is 10 sqft.";
    if (formData.size_sqft > 10_000_000) errors.size_sqft = "Maximum size is 10 million sqft.";
    if (formData.age_years < 0) errors.age_years = "Age cannot be negative.";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!validate()) return;

    setStatus("evaluating");
    setActiveStep(0);
    setResult(null);
    setErrorMessage("");
    setAuditExpanded(false);

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${baseUrl}/api/v1/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (!response.ok) {
        const body: unknown = await response.json().catch(() => null);
        const detail =
          typeof body === "object" &&
          body !== null &&
          "detail" in body &&
          typeof body.detail === "string"
            ? body.detail
            : `API returned status ${response.status}.`;
        throw new Error(detail);
      }
      setResult((await response.json()) as ValuationResult);
      setStatus("complete");
    } catch (error: unknown) {
      console.error(error);
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Could not connect to the API. Is the backend running?",
      );
      setStatus("error");
    }
  };

  const format = (value: number) => value.toLocaleString("en-US");

  return (
    <main>
      <nav className="site-nav page-width">
        <a className="brand" href="#home" aria-label="Oracle Flow home">
          <span>
            <strong>Oracle Flow</strong>
            <small>The real estate valuation engine</small>
          </span>
        </a>
        <a
          className="github-link"
          href="https://github.com/R123456-123/oracle-flow"
          target="_blank"
          rel="noreferrer"
        >
          <svg aria-hidden="true" className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 .7a11.3 11.3 0 0 0-3.6 22c.57.1.78-.25.78-.55v-2.1c-3.18.7-3.85-1.35-3.85-1.35-.52-1.32-1.27-1.67-1.27-1.67-1.04-.71.08-.7.08-.7 1.15.08 1.75 1.18 1.75 1.18 1.02 1.75 2.67 1.25 3.32.96.1-.74.4-1.25.72-1.54-2.54-.29-5.2-1.27-5.2-5.66 0-1.25.45-2.27 1.18-3.07-.12-.29-.51-1.46.11-3.03 0 0 .96-.31 3.13 1.17a10.8 10.8 0 0 1 5.7 0c2.17-1.48 3.13-1.17 3.13-1.17.62 1.57.23 2.74.11 3.03.73.8 1.18 1.82 1.18 3.07 0 4.4-2.67 5.36-5.21 5.65.41.36.77 1.08.77 2.18v3.23c0 .3.2.66.78.55A11.3 11.3 0 0 0 12 .7Z" />
          </svg>
          <span className="hidden sm:inline">View on GitHub</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </a>
      </nav>

      <section id="home" className="hero page-width">
        <div className="hero-copy">
          <p className="overline">AI PROPERTY VALUATION</p>
          <h1>Understand the value<br /><em>behind a property.</em></h1>
          <p className="hero-description">
            Oracle Flow is a multi-agent real estate valuation engine that turns property
            details into explainable value ranges, liquidity signals, and safety-reviewed decisions.
          </p>
          <a className="hero-cta" href="#workspace">Start an evaluation <ArrowRight className="h-4 w-4" /></a>
        </div>
      </section>

      <section id="workspace" className="page-width workspace-section">
        <SectionHeading eyebrow="THE WORKSPACE" title="Evaluate a property" description="Give the engine a few facts. Get a clear, structured view of value." />
        <div className="workspace-grid">
          <InputCard
            formData={formData}
            errors={formErrors}
            status={status}
            updateField={updateField}
            onSubmit={handleSubmit}
          />
          <OutputCard
            status={status}
            result={result}
            activeStep={activeStep}
            auditExpanded={auditExpanded}
            setAuditExpanded={setAuditExpanded}
            errorMessage={errorMessage}
            format={format}
          />
        </div>
      </section>

      <section id="how-it-works" className="how-section">
        <div className="page-width">
          <SectionHeading eyebrow="HOW IT WORKS" title="Reasoned in three focused steps" description="Small, understandable agents. Clear responsibilities. A final answer you can inspect." />
          <div className="steps-grid">
            {steps.map(([number, title, description]) => (
              <div className="step-card" key={number}>
                <span className="step-number">{number}</span>
                <div className="step-icon">{number === "01" ? <ScanSearch /> : number === "02" ? <TrendingUp /> : <ShieldCheck />}</div>
                <h3>{title}</h3>
                <p>{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="roadmap-section page-width">
        <SectionHeading eyebrow="THE ROAD AHEAD" title="Built in phases" description="A solid first foundation, with a clear path toward production intelligence." />
        <div className="roadmap-grid">
          <RoadmapCard phase="Phase 1" title="The foundation" active items={["Typed FastAPI service", "Multi-agent valuation flow", "Prompt injection guardrails", "Responsive evaluation workspace"]} />
          <RoadmapCard phase="Phase 2" title="Deeper intelligence" items={["Comparable market data", "Evaluation history and persistence", "Monitoring and observability", "Authentication and production scale"]} />
        </div>
      </section>

      <footer className="site-footer page-width">
        <a className="brand" href="#home"><span><strong>Oracle Flow</strong><small>The real estate valuation engine</small></span></a>
        <p>AI-assisted analysis. Human-informed decisions.</p>
      </footer>
    </main>
  );
}

function SectionHeading({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return (
    <div className="section-heading">
      <p className="overline">{eyebrow}</p>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}

function InputCard({ formData, errors, status, updateField, onSubmit }: { formData: { address: string; property_type: string; size_sqft: number; age_years: number; has_legal_disputes: boolean }; errors: Record<string, string>; status: Status; updateField: (field: keyof typeof formData, value: string | number | boolean) => void; onSubmit: (event: React.FormEvent<HTMLFormElement>) => void }) {
  return (
    <div className="panel input-panel">
      <div className="panel-heading"><div><p className="overline">PROPERTY INPUT</p><h3>Start with the basics</h3></div><Layers3 className="panel-heading-icon" /></div>
      <form onSubmit={onSubmit} className="input-form">
        <InputField label="Property address" error={errors.address}><input className="dashboard-input" value={formData.address} onChange={(event) => updateField("address", event.target.value)} placeholder="e.g. 123 Main Street" required /></InputField>
        <InputField label="Property type" error={errors.property_type}><input className="dashboard-input" value={formData.property_type} onChange={(event) => updateField("property_type", event.target.value)} placeholder="e.g. Apartment" required /></InputField>
        <div className="input-pair">
          <InputField label="Size (sqft)" error={errors.size_sqft}><input className="dashboard-input" type="number" min="10" value={formData.size_sqft} onChange={(event) => updateField("size_sqft", Number(event.target.value))} required /></InputField>
          <InputField label="Age (years)" error={errors.age_years}><input className="dashboard-input" type="number" min="0" value={formData.age_years} onChange={(event) => updateField("age_years", Number(event.target.value))} required /></InputField>
        </div>
        <label className="legal-toggle"><input type="checkbox" checked={formData.has_legal_disputes} onChange={(event) => updateField("has_legal_disputes", event.target.checked)} /><span><strong>Known legal disputes</strong><small>Include this risk in the review</small></span></label>
        <button className="primary-button" type="submit" disabled={status === "evaluating"}>{status === "evaluating" ? <><span className="button-spinner" /> Reviewing property</> : <>Generate valuation <ArrowRight className="h-4 w-4" /></>}</button>
      </form>
      <p className="panel-note"><ShieldCheck className="h-3.5 w-3.5" /> Your input is screened before it reaches the valuation agents.</p>
    </div>
  );
}

function InputField({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return <label className="input-field"><span>{label}</span>{children}{error && <small className="field-error">{error}</small>}</label>;
}

function OutputCard({ status, result, activeStep, auditExpanded, setAuditExpanded, errorMessage, format }: { status: Status; result: ValuationResult | null; activeStep: number; auditExpanded: boolean; setAuditExpanded: (value: boolean) => void; errorMessage: string; format: (value: number) => string }) {
  const audit = result?.oversight_audit_log;
  return (
    <div className="panel output-panel">
      <div className="panel-heading"><div><p className="overline">ENGINE OUTPUT</p><h3>{status === "complete" ? "Your valuation overview" : "Your answer will appear here"}</h3></div><StatusBadge status={status} safe={result?.is_safe_to_process} /></div>
      {status === "idle" && <div className="output-empty"><div className="empty-symbol"><Target /></div><h4>Ready to evaluate</h4><p>Submit a property to see its market range, liquidity signal, and safety review.</p></div>}
      {status === "evaluating" && <div className="progress-list">{["Researcher agent", "Actor agent", "Evaluator / Judge"].map((label, index) => <div className={`progress-row ${index < activeStep ? "done" : ""}`} key={label}><span>{index < activeStep ? <CheckCircle2 /> : index + 1}</span><p>{label}</p><small>{index < activeStep ? "Complete" : index === activeStep ? "Working..." : "Queued"}</small></div>)}</div>}
      {status === "error" && <div className="error-box"><AlertCircle /><div><h4>Evaluation could not complete</h4><p>{errorMessage}</p></div></div>}
      {status === "complete" && result && <Result result={result} format={format} />}
      {status === "complete" && result && audit && <div className="audit-wrap"><button className="audit-toggle" onClick={() => setAuditExpanded(!auditExpanded)}><span><ShieldCheck className="h-4 w-4" /> Oversight audit</span><ChevronDown className={auditExpanded ? "rotate-180" : ""} /></button>{auditExpanded && <div className="audit-content"><div className="audit-pills"><AuditPill label="Injection" value={audit.prompt_injection_detected ? "Detected" : "Clear"} danger={audit.prompt_injection_detected} /><AuditPill label="Hallucination" value={audit.hallucination_check} danger={audit.hallucination_check !== "passed"} /><AuditPill label="Bias review" value={audit.bias_or_unsubstantiated_premium_flagged ? "Flagged" : "Clear"} danger={audit.bias_or_unsubstantiated_premium_flagged} /></div>{audit.flagged_risks.length > 0 && <div className="audit-tags">{audit.flagged_risks.map((risk) => <span key={risk}>{risk}</span>)}</div>}</div>}</div>}
    </div>
  );
}

function Result({ result, format }: { result: ValuationResult; format: (value: number) => string }) {
  if (!result.is_safe_to_process) return <div className="rejected-box"><AlertTriangle /><div><h4>Evaluation rejected</h4><p>{result.refusal_reason}</p></div></div>;
  return <div className="result-content"><div className="market-value"><p><TrendingUp className="h-4 w-4" /> Estimated market range</p><strong>${format(result.market_value_range[0])}<span>—</span>${format(result.market_value_range[1])}</strong><small>AI-generated range · not a certified appraisal</small></div><div className="result-metrics"><Metric icon={<TrendingUp />} label="Distress range" value={`$${format(result.distress_value_range[0])} – $${format(result.distress_value_range[1])}`} /><Metric icon={<Target />} label="Resale potential" value={`${result.resale_potential_index}/100`} /><Metric icon={<Clock3 />} label="Estimated sale" value={`${result.estimated_time_to_sell_days[0]}–${result.estimated_time_to_sell_days[1]} days`} /></div><div className="confidence"><span><ShieldCheck /> Judge confidence</span><strong>{Math.round(result.agent_confidence_score * 100)}%</strong></div><div className="confidence-bar"><span style={{ width: `${result.agent_confidence_score * 100}%` }} /></div></div>;
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return <div className="metric-card"><span>{icon}{label}</span><strong>{value}</strong></div>;
}

function StatusBadge({ status, safe }: { status: Status; safe?: boolean }) {
  if (status === "evaluating") return <span className="status-badge status-blue">Reviewing</span>;
  if (status === "complete" && safe) return <span className="status-badge status-green"><CheckCircle2 /> Complete</span>;
  if (status === "complete") return <span className="status-badge status-red"><AlertTriangle /> Rejected</span>;
  if (status === "error") return <span className="status-badge status-red">Error</span>;
  return <span className="status-badge status-neutral">Awaiting input</span>;
}

function AuditPill({ label, value, danger }: { label: string; value: string; danger: boolean }) {
  return <span className={`audit-pill ${danger ? "audit-danger" : "audit-good"}`}>{label}: {value}</span>;
}

function RoadmapCard({ phase, title, items, active = false }: { phase: string; title: string; items: string[]; active?: boolean }) {
  return <div className={`roadmap-card ${active ? "roadmap-active" : ""}`}><div className="roadmap-top"><span>{phase}</span>{active && <small>Current</small>}</div><h3>{title}</h3><ul>{items.map((item) => <li key={item}><CheckCircle2 />{item}</li>)}</ul></div>;
}
