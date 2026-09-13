import React, { useEffect, useRef, useState } from "react";
import { analyzeFile, analyzeText, getRoles } from "../api";
import AnalysisResult from "../components/AnalysisResult";

const SAMPLE = `Jane Smith
jane.smith@email.com | +1 555 987 6543 | linkedin.com/in/janesmith

Summary
Detail-oriented Frontend Developer with 4 years of experience building responsive,
accessible web applications with React and TypeScript.

Skills
JavaScript, TypeScript, React, Redux, HTML, CSS, Sass, Jest, Webpack, Git, Accessibility

Experience
Frontend Developer — BrightApps (2021–Present)
- Built and shipped a component library used across 6 product teams
- Improved Lighthouse performance score from 62 to 95
- Led migration from JavaScript to TypeScript, reducing runtime errors by 30%

Education
Bachelor's Degree in Computer Science — State University

Projects
- Open-source React data-table with 1.2k GitHub stars`;

export default function Analyze() {
  const [tab, setTab] = useState("upload"); // 'upload' | 'paste'
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [roles, setRoles] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const inputRef = useRef(null);

  useEffect(() => {
    getRoles().then((d) => setRoles(d.roles || [])).catch(() => setRoles([]));
  }, []);

  const pickFile = (f) => {
    if (!f) return;
    const ok = /\.(pdf|docx|txt)$/i.test(f.name);
    if (!ok) {
      setError("Please choose a PDF, DOCX, or TXT file.");
      return;
    }
    setError("");
    setFile(f);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    pickFile(e.dataTransfer.files[0]);
  };

  const submit = async () => {
    setError("");
    setLoading(true);
    setResult(null);
    try {
      let data;
      if (tab === "upload") {
        if (!file) throw new Error("Please select a resume file first.");
        data = await analyzeFile(file, targetRole);
      } else {
        if (text.trim().length < 30) throw new Error("Please paste a longer resume (30+ characters).");
        data = await analyzeText(text, targetRole);
      }
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container section">
      <div className="section-title" style={{ marginBottom: "2rem" }}>
        <h2>Resume Analyzer</h2>
        <p>Upload or paste your resume, pick a target role, and get instant NLP-based feedback.</p>
      </div>

      <div className="analyze-layout">
        {/* ---------- Input panel ---------- */}
        <div className="card upload-panel">
          <div className="tabs">
            <button className={`tab ${tab === "upload" ? "active" : ""}`} onClick={() => setTab("upload")}>
              Upload File
            </button>
            <button className={`tab ${tab === "paste" ? "active" : ""}`} onClick={() => setTab("paste")}>
              Paste Text
            </button>
          </div>

          {tab === "upload" ? (
            <div
              className={`dropzone ${dragging ? "drag" : ""}`}
              onClick={() => inputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
            >
              <div className="dz-icon">📄</div>
              {file ? (
                <p className="dz-file" style={{ margin: "0.5rem 0 0" }}>{file.name}</p>
              ) : (
                <>
                  <p style={{ margin: "0.5rem 0 0.2rem", fontWeight: 600, color: "var(--text)" }}>
                    Drop your resume here
                  </p>
                  <p style={{ margin: 0, fontSize: "0.85rem" }}>or click to browse · PDF, DOCX, TXT</p>
                </>
              )}
              <input
                ref={inputRef} type="file" accept=".pdf,.docx,.txt" hidden
                onChange={(e) => pickFile(e.target.files[0])}
              />
            </div>
          ) : (
            <>
              <textarea
                className="resume-input"
                placeholder="Paste your resume text here..."
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
              <button
                className="btn btn-ghost"
                style={{ marginTop: "0.6rem", width: "100%" }}
                onClick={() => setText(SAMPLE)}
              >
                Try a sample resume
              </button>
            </>
          )}

          <label className="field-label">Target role (optional)</label>
          <select className="role-select" value={targetRole} onChange={(e) => setTargetRole(e.target.value)}>
            <option value="">Auto-detect best match</option>
            {roles.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>

          {error && <div className="alert alert-error" style={{ marginTop: "1rem" }}>{error}</div>}

          <button
            className="btn btn-primary btn-lg"
            style={{ width: "100%", marginTop: "1.2rem", justifyContent: "center" }}
            onClick={submit}
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Analyze Resume"}
          </button>
        </div>

        {/* ---------- Results panel ---------- */}
        <div>
          {loading && (
            <div className="card">
              <div className="spinner" />
              <p style={{ textAlign: "center", marginTop: "1rem" }}>Running NLP analysis…</p>
            </div>
          )}
          {!loading && !result && (
            <div className="card results-empty">
              <div className="big">📊</div>
              <h3>Your analysis will appear here</h3>
              <p>Submit a resume to see your score, matched roles, and improvement tips.</p>
            </div>
          )}
          {!loading && result && <AnalysisResult data={result} />}
        </div>
      </div>
    </div>
  );
}
