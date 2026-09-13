import React from "react";
import ScoreGauge from "./ScoreGauge";

const BREAKDOWN_LABELS = {
  skills: "Skills Coverage",
  sections: "Resume Sections",
  experience: "Experience",
  readability: "Readability & Impact",
  keyword_match: "Job Keyword Match",
};

function Bar({ value }) {
  return (
    <div className="bar">
      <span style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
    </div>
  );
}

function verdict(score) {
  if (score >= 80) return { text: "Excellent — your resume is highly competitive.", cls: "ok" };
  if (score >= 65) return { text: "Good — a few tweaks will make it stronger.", cls: "ok" };
  if (score >= 45) return { text: "Fair — several areas need improvement.", cls: "warn" };
  return { text: "Needs work — follow the suggestions below.", cls: "warn" };
}

export default function AnalysisResult({ data }) {
  const ex = data.extracted;
  const v = verdict(data.overall_score);

  const best = data.best_fit;

  return (
    <div>
      {/* Best-fit role banner */}
      {best && (
        <div className="best-fit result-card">
          <div className="bf-left">
            <span className="bf-label">🏆 Best-fit role</span>
            <div className="bf-role">{best.role}</div>
            <div className="bf-sub">{best.category} · {best.experience_level} level</div>
            {best.matched_skills.length > 0 && (
              <div className="bf-skills">
                Matches {best.matched_skills.length} of{" "}
                {best.matched_skills.length + best.missing_skills.length} key skills
              </div>
            )}
          </div>
          <div className="bf-gauge">
            <div className="bf-pct">{best.suitability}%</div>
            <div className="bf-pct-label">suitable</div>
          </div>
        </div>
      )}

      {/* Score overview */}
      <div className="card result-card">
        <div className="score-hero">
          <ScoreGauge score={data.overall_score} />
          <div style={{ flex: 1, minWidth: 220 }}>
            <h3 style={{ marginBottom: 4 }}>Overall Resume Score</h3>
            <p style={{ margin: "0 0 12px" }}>
              <span className={`chip ${v.cls}`}>{v.text}</span>
            </p>
            <div className="chips">
              <span className="chip muted">{ex.skills_count} skills found</span>
              <span className="chip muted">{ex.word_count} words</span>
              <span className="chip muted">{ex.estimated_experience_years} yrs experience</span>
              <span className="chip muted">{ex.sections_found.length} sections</span>
            </div>
          </div>
        </div>

        <hr style={{ border: "none", borderTop: "1px solid var(--border)", margin: "1.4rem 0" }} />

        {Object.entries(data.score_breakdown).map(([key, val]) => (
          <div className="breakdown-row" key={key}>
            <div className="top">
              <span>{BREAKDOWN_LABELS[key] || key}</span>
              <span>{val}%</span>
            </div>
            <Bar value={val} />
          </div>
        ))}
      </div>

      {/* Skills */}
      <div className="card result-card">
        <h3>🧠 Extracted Skills</h3>
        {ex.skills_found.length ? (
          <div className="chips">
            {ex.skills_found.map((s) => (
              <span className="chip" key={s}>{s}</span>
            ))}
          </div>
        ) : (
          <p>No recognizable skills were detected. Add a dedicated Skills section.</p>
        )}
      </div>

      {/* Top skills by demand */}
      {data.top_skills_by_demand.length > 0 && (
        <div className="card result-card">
          <h3>📈 Your Skills by Market Demand</h3>
          {data.top_skills_by_demand.map((s) => (
            <div className="demand-row" key={s.skill}>
              <span className="name">{s.skill}</span>
              <Bar value={s.demand} />
              <span className="val">{s.demand}</span>
            </div>
          ))}
        </div>
      )}

      {/* Job matches */}
      <div className="card result-card">
        <h3>🎯 Roles You're Most Suitable For</h3>
        <p style={{ marginTop: 0 }}>
          Ranked by suitability — a blend of skill coverage and NLP similarity across 1,500 job roles.
        </p>
        {data.job_matches.map((job, i) => (
          <div className="job-match" key={i}>
            <div className="jm-head">
              <div>
                <div className="jm-title">{job.role}</div>
                <div className="jm-cat">{job.category} · {job.experience_level} level</div>
              </div>
              <div className="match-pill">
                {job.suitability}%
                <span className="match-pill-label">suitable</span>
              </div>
            </div>
            {job.matched_skills.length > 0 && (
              <div className="chips" style={{ marginTop: 10 }}>
                {job.matched_skills.map((s) => (
                  <span className="chip ok" key={s}>✓ {s}</span>
                ))}
              </div>
            )}
            {job.missing_skills.length > 0 && (
              <div className="chips" style={{ marginTop: 8 }}>
                {job.missing_skills.map((s) => (
                  <span className="chip warn" key={s}>+ {s}</span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Skill gap */}
      {data.skill_gap && data.skill_gap.target_role && (
        <div className="card result-card">
          <h3>🔍 Skill Gap — {data.skill_gap.target_role}</h3>
          <p style={{ marginTop: 0 }}><strong style={{ color: "var(--success)" }}>You have:</strong></p>
          <div className="chips">
            {data.skill_gap.have.length
              ? data.skill_gap.have.map((s) => <span className="chip ok" key={s}>{s}</span>)
              : <span className="chip muted">None matched yet</span>}
          </div>
          <p style={{ margin: "1rem 0 0.4rem" }}><strong style={{ color: "var(--warning)" }}>Consider adding:</strong></p>
          <div className="chips">
            {data.skill_gap.missing.length
              ? data.skill_gap.missing.map((s) => <span className="chip warn" key={s}>{s}</span>)
              : <span className="chip ok">You cover all key skills! 🎉</span>}
          </div>
        </div>
      )}

      {/* Suggestions */}
      <div className="card result-card">
        <h3>💡 Suggestions to Improve</h3>
        <ul className="suggestion-list">
          {data.suggestions.map((s, i) => (
            <li key={i}><span className="dot">→</span><span>{s}</span></li>
          ))}
        </ul>
      </div>
    </div>
  );
}
