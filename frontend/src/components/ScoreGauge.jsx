import React from "react";

// Circular SVG gauge for the overall score (0-100).
export default function ScoreGauge({ score }) {
  const radius = 65;
  const stroke = 12;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const color =
    score >= 75 ? "#16a34a" : score >= 50 ? "#d97706" : "#dc2626";

  return (
    <div className="gauge">
      <svg width="150" height="150" viewBox="0 0 150 150">
        <circle
          cx="75" cy="75" r={radius} fill="none"
          stroke="#e2e8f0" strokeWidth={stroke}
        />
        <circle
          cx="75" cy="75" r={radius} fill="none"
          stroke={color} strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          transform="rotate(-90 75 75)"
          style={{ transition: "stroke-dashoffset 0.9s ease" }}
        />
      </svg>
      <div className="score-num" style={{ color }}>
        {score}
        <small>/ 100</small>
      </div>
    </div>
  );
}
