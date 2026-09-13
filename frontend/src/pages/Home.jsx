import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getStats } from "../api";

const FEATURES = [
  { icon: "🧠", title: "NLP Skill Extraction", desc: "Detects 240+ technical and soft skills from your resume text using tokenization and phrase matching." },
  { icon: "🎯", title: "Job Role Matching", desc: "TF-IDF + cosine similarity ranks your resume against 1,500 real-world job descriptions." },
  { icon: "📊", title: "Weighted Scoring", desc: "Five scored dimensions — skills, sections, experience, readability and keyword match." },
  { icon: "🔍", title: "Skill Gap Analysis", desc: "See exactly which in-demand skills you're missing for your target role." },
  { icon: "💡", title: "Actionable Tips", desc: "Concrete, prioritized suggestions to make your resume stronger." },
  { icon: "🔒", title: "Private & Offline", desc: "Analysis runs locally on the server. No third-party API, no data leaves the app." },
];

function StatCard({ num, label }) {
  return (
    <div className="stat-card">
      <div className="num">{num}</div>
      <div className="label">{label}</div>
    </div>
  );
}

export default function Home() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getStats().then(setStats).catch(() => setStats(null));
  }, []);

  return (
    <>
      <section className="hero">
        <div className="container hero-center">
          <span className="hero-tag">⚡ NLP-Powered · React + Flask</span>
          <h1>
            Analyze your resume with <span className="highlight">AI precision</span>
          </h1>
          <p>
            Upload your resume and get an instant, data-driven score, skill breakdown,
            matching job roles, and personalized suggestions — all powered by natural
            language processing.
          </p>
          <div className="hero-actions">
            <Link to="/analyze" className="btn btn-primary btn-lg">Analyze My Resume →</Link>
            <Link to="/about" className="btn btn-ghost btn-lg">How it works</Link>
          </div>
        </div>
      </section>

      <div className="container">
        <div className="stats-strip">
          <StatCard num={stats ? stats.job_roles.toLocaleString() : "1,500"} label="Job Roles" />
          <StatCard num={stats ? stats.unique_skills : "240"} label="Skills Tracked" />
          <StatCard num={stats ? stats.resume_samples.toLocaleString() : "1,000"} label="Resume Samples" />
          <StatCard num={stats ? stats.categories : "7"} label="Industry Categories" />
        </div>
      </div>

      <section className="section">
        <div className="container">
          <div className="section-title">
            <h2>Everything you need to stand out</h2>
            <p>A complete analysis toolkit built on classic, explainable NLP techniques.</p>
          </div>
          <div className="grid-3">
            {FEATURES.map((f) => (
              <div className="card" key={f.title}>
                <div className="feature-icon">{f.icon}</div>
                <h3>{f.title}</h3>
                <p style={{ margin: 0 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="card" style={{ textAlign: "center", background: "linear-gradient(135deg, var(--primary-soft), #fff)" }}>
            <h2>Ready to see your score?</h2>
            <p style={{ maxWidth: 480, margin: "0.5rem auto 1.5rem" }}>
              It takes less than 10 seconds. Upload a PDF, DOCX, or just paste your text.
            </p>
            <Link to="/analyze" className="btn btn-primary btn-lg">Get Started Free</Link>
          </div>
        </div>
      </section>
    </>
  );
}
