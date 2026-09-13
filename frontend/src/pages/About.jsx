import React from "react";
import { Link } from "react-router-dom";

const STEPS = [
  { n: 1, title: "Text Extraction", desc: "Your PDF, DOCX, or pasted text is parsed into clean plain text on the server." },
  { n: 2, title: "Tokenization & Cleaning", desc: "The text is lowercased, tokenized, and stripped of stopwords for analysis." },
  { n: 3, title: "Skill & Section Detection", desc: "Word-boundary phrase matching finds skills against a 240+ skill vocabulary; header keywords detect resume sections." },
  { n: 4, title: "Job Matching (TF-IDF)", desc: "Your resume is vectorized and compared with 1,500 job descriptions using cosine similarity to rank the best-fit roles." },
  { n: 5, title: "Scoring & Suggestions", desc: "Five weighted dimensions produce an overall score, plus a skill-gap report and prioritized improvement tips." },
];

export default function About() {
  return (
    <div className="container section">
      <div className="section-title">
        <h2>How it works</h2>
        <p>A transparent, explainable NLP pipeline — no black-box LLM, no data sent to third parties.</p>
      </div>

      <div style={{ maxWidth: 760, margin: "0 auto" }}>
        <div className="card">
          {STEPS.map((s) => (
            <div className="about-step" key={s.n}>
              <div className="n">{s.n}</div>
              <div>
                <h3 style={{ marginBottom: 4 }}>{s.title}</h3>
                <p style={{ margin: 0 }}>{s.desc}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="card" style={{ marginTop: "1.5rem" }}>
          <h3>The tech stack</h3>
          <div className="chips" style={{ marginTop: "0.6rem" }}>
            {["React", "React Router", "Flask", "scikit-learn (TF-IDF)", "pandas", "pdfplumber", "python-docx"].map((t) => (
              <span className="chip" key={t}>{t}</span>
            ))}
          </div>
          <p style={{ marginTop: "1rem" }}>
            The backend ships with three consistent datasets — <strong>1,500 job roles</strong>,
            <strong> 1,500 skill mappings</strong>, and <strong>1,000+ resume samples</strong> —
            each with the same 5-column structure, powering the matching and scoring engine.
          </p>
        </div>

        <div style={{ textAlign: "center", marginTop: "2rem" }}>
          <Link to="/analyze" className="btn btn-primary btn-lg">Analyze My Resume →</Link>
        </div>
      </div>
    </div>
  );
}
