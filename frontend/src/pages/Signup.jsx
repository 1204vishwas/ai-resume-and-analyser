import React, { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function strength(pw) {
  let score = 0;
  if (pw.length >= 6) score++;
  if (pw.length >= 10) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/\d/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return Math.min(score, 4); // 0-4
}

const STRENGTH_LABEL = ["", "Weak", "Fair", "Good", "Strong"];
const STRENGTH_COLOR = ["#e2e8f0", "#dc2626", "#d97706", "#16a34a", "#16a34a"];

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const pwScore = useMemo(() => strength(password), [password]);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (password.length < 6) return setError("Password must be at least 6 characters long.");
    if (password !== confirm) return setError("Passwords do not match.");
    setLoading(true);
    try {
      await signup(name, email, password);
      navigate("/analyze", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <aside className="auth-brand">
        <div className="auth-brand-inner">
          <div className="brand" style={{ color: "#fff" }}>
            <span className="brand-badge">AI</span>
            <span>Resume Analyzer</span>
          </div>
          <h2>Create your account</h2>
          <p>Join in seconds and get instant, NLP-powered feedback on your resume.</p>
          <ul className="auth-points">
            <li>✓ Free and private — analysis runs locally</li>
            <li>✓ Score, skills, and job matches instantly</li>
            <li>✓ Actionable tips to improve your resume</li>
          </ul>
        </div>
      </aside>

      <div className="auth-form-wrap">
        <form className="auth-card" onSubmit={submit}>
          <h1>Sign up</h1>
          <p className="auth-sub">Start analyzing your resume today.</p>

          {error && <div className="alert alert-error">{error}</div>}

          <label className="field-label" htmlFor="name">Full name</label>
          <input
            id="name" type="text" className="auth-input" autoComplete="name"
            placeholder="Jane Smith" value={name}
            onChange={(e) => setName(e.target.value)} required
          />

          <label className="field-label" htmlFor="email">Email address</label>
          <input
            id="email" type="email" className="auth-input" autoComplete="email"
            placeholder="you@example.com" value={email}
            onChange={(e) => setEmail(e.target.value)} required
          />

          <label className="field-label" htmlFor="password">Password</label>
          <div className="pw-wrap">
            <input
              id="password" type={showPw ? "text" : "password"} className="auth-input"
              autoComplete="new-password" placeholder="At least 6 characters" value={password}
              onChange={(e) => setPassword(e.target.value)} required
            />
            <button type="button" className="pw-toggle" onClick={() => setShowPw((s) => !s)}>
              {showPw ? "Hide" : "Show"}
            </button>
          </div>
          {password && (
            <div className="pw-meter">
              <div className="pw-meter-bar">
                <span style={{ width: `${(pwScore / 4) * 100}%`, background: STRENGTH_COLOR[pwScore] }} />
              </div>
              <span className="pw-meter-label" style={{ color: STRENGTH_COLOR[pwScore] }}>
                {STRENGTH_LABEL[pwScore]}
              </span>
            </div>
          )}

          <label className="field-label" htmlFor="confirm">Confirm password</label>
          <input
            id="confirm" type={showPw ? "text" : "password"} className="auth-input"
            autoComplete="new-password" placeholder="Re-enter your password" value={confirm}
            onChange={(e) => setConfirm(e.target.value)} required
          />

          <button className="btn btn-primary btn-lg" style={{ width: "100%", justifyContent: "center", marginTop: "1.4rem" }} disabled={loading}>
            {loading ? "Creating account…" : "Create account"}
          </button>

          <p className="auth-switch">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
