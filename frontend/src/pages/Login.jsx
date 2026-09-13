import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from || "/analyze";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate(redirectTo, { replace: true });
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
          <h2>Welcome back 👋</h2>
          <p>Sign in to analyze resumes, track your scores, and discover your best-matching roles.</p>
          <ul className="auth-points">
            <li>✓ NLP-powered resume scoring</li>
            <li>✓ Job matching across 1,500 roles</li>
            <li>✓ Personalized skill-gap insights</li>
          </ul>
        </div>
      </aside>

      <div className="auth-form-wrap">
        <form className="auth-card" onSubmit={submit}>
          <h1>Sign in</h1>
          <p className="auth-sub">Enter your credentials to continue.</p>

          {error && <div className="alert alert-error">{error}</div>}

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
              autoComplete="current-password" placeholder="••••••••" value={password}
              onChange={(e) => setPassword(e.target.value)} required
            />
            <button type="button" className="pw-toggle" onClick={() => setShowPw((s) => !s)}>
              {showPw ? "Hide" : "Show"}
            </button>
          </div>

          <button className="btn btn-primary btn-lg" style={{ width: "100%", justifyContent: "center", marginTop: "1.4rem" }} disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </button>

          <p className="auth-switch">
            Don&apos;t have an account? <Link to="/signup">Create one</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
