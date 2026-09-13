import React from "react";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div className="brand">
          <span className="brand-badge">AI</span>
          <span>Resume Analyzer</span>
        </div>
        <p style={{ margin: 0, color: "#94a3b8" }}>
          NLP-powered resume analysis · Built with React &amp; Flask
        </p>
        <p style={{ margin: 0, color: "#64748b", fontSize: "0.85rem" }}>
          © {new Date().getFullYear()} Resume Analyzer
        </p>
      </div>
    </footer>
  );
}
