"""Core NLP analysis pipeline for a resume."""
import re

from sklearn.metrics.pairwise import cosine_similarity

from config import Config
from nlp.data_store import store

# Resume section headers we try to detect
SECTION_KEYWORDS = {
    "contact": ["email", "phone", "@", "linkedin", "github"],
    "summary": ["summary", "objective", "profile", "about me"],
    "experience": ["experience", "employment", "work history", "professional experience"],
    "education": ["education", "academic", "university", "bachelor", "master", "degree"],
    "skills": ["skills", "technical skills", "competencies", "technologies"],
    "projects": ["projects", "portfolio", "personal projects"],
    "certifications": ["certification", "certificate", "licensed", "credential"],
}

ACTION_VERBS = {
    "led", "built", "designed", "developed", "created", "managed", "implemented",
    "improved", "increased", "reduced", "launched", "delivered", "optimized",
    "architected", "automated", "collaborated", "mentored", "achieved", "drove",
}

EMAIL_RE = re.compile(r"[\w.\-+]+@[\w\-]+\.[\w.\-]+")
PHONE_RE = re.compile(r"(\+?\d[\d\s().\-]{7,}\d)")
YEARS_RE = re.compile(r"(\d{1,2})\+?\s*(?:years|yrs)", re.IGNORECASE)


def analyze_resume(text, target_role=None):
    """Run the full analysis and return a JSON-serializable dict."""
    text = text or ""
    lower = text.lower()
    words = re.findall(r"[a-zA-Z][a-zA-Z+#.]*", text)
    word_count = len(words)

    skills_found = _extract_skills(lower)
    sections = _detect_sections(lower)
    experience_years = _estimate_experience(lower)
    contact = _contact_info(text)
    action_verb_count = sum(1 for w in words if w.lower() in ACTION_VERBS)

    job_matches = _match_jobs(text, skills_found)
    skill_gap = _skill_gap(skills_found, target_role, job_matches)
    breakdown = _score(text, word_count, skills_found, sections,
                       experience_years, action_verb_count, job_matches)
    overall = round(sum(breakdown.values()) / len(breakdown))
    suggestions = _suggestions(sections, skills_found, word_count,
                               action_verb_count, contact, skill_gap, breakdown)

    return {
        "overall_score": overall,
        "score_breakdown": breakdown,
        "extracted": {
            "skills_found": [store.skill_canonical.get(s, s) for s in skills_found],
            "skills_count": len(skills_found),
            "sections_found": sorted(sections),
            "word_count": word_count,
            "estimated_experience_years": experience_years,
            "action_verbs_used": action_verb_count,
            "has_email": bool(contact["email"]),
            "has_phone": bool(contact["phone"]),
        },
        "best_fit": job_matches[0] if job_matches else None,
        "job_matches": job_matches,
        "skill_gap": skill_gap,
        "suggestions": suggestions,
        "top_skills_by_demand": _top_demand_skills(skills_found),
    }


# --------------------------------------------------------------------------
def _extract_skills(lower_text):
    """Return sorted list of lowercase skill keys present in the text."""
    found = []
    for key in store.skill_canonical:
        # word-boundary match; escape regex specials (C++, C#, Node.js ...)
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(key) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, lower_text):
            found.append(key)
    return sorted(set(found))


def _detect_sections(lower_text):
    found = set()
    for section, keywords in SECTION_KEYWORDS.items():
        if any(kw in lower_text for kw in keywords):
            found.add(section)
    return found


def _estimate_experience(lower_text):
    matches = [int(m) for m in YEARS_RE.findall(lower_text)]
    matches = [m for m in matches if m <= 40]
    return max(matches) if matches else 0


def _contact_info(text):
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    return {
        "email": email.group(0) if email else "",
        "phone": phone.group(0).strip() if phone else "",
    }


SENIORITY_PREFIXES = ("Intern", "Junior", "Mid-level", "Senior", "Lead", "Principal")


def _base_role(title):
    """Strip a leading seniority word so the headline shows the role itself."""
    for prefix in SENIORITY_PREFIXES:
        if title.startswith(prefix + " "):
            return title[len(prefix) + 1:]
    return title


def _suitability(cosine, matched, missing):
    """Blend skill coverage (60%) and text similarity (40%) into a 0-100 %."""
    total = len(matched) + len(missing)
    skill_ratio = (len(matched) / total) if total else 0.0
    sim_component = min(1.0, cosine / 0.5)  # cosine ~0-0.5 -> 0-1
    return round(100 * (0.6 * skill_ratio + 0.4 * sim_component))


def _match_jobs(text, skills_found):
    vec = store.vectorizer.transform([text])
    sims = cosine_similarity(vec, store.job_matrix)[0]
    order = sims.argsort()[::-1]

    # Keep the best-matching posting per DISTINCT base role (first seen along
    # the similarity-sorted order is that role's strongest posting).
    role_best = {}
    for idx in order:
        role = _base_role(str(store.jobs.iloc[idx]["title"]))
        if role not in role_best:
            role_best[role] = idx
        if len(role_best) >= 12:
            break

    found_set = set(skills_found)
    results = []
    for role, idx in role_best.items():
        required = store.job_required[idx]
        matched = [s for s in required if s.lower() in found_set]
        missing = [s for s in required if s.lower() not in found_set]
        results.append({
            "job_title": store.jobs.iloc[idx]["title"],
            "role": role,
            "category": store.jobs.iloc[idx]["category"],
            "experience_level": store.jobs.iloc[idx]["level"],
            "similarity": round(float(sims[idx]) * 100, 1),
            "suitability": _suitability(float(sims[idx]), matched, missing),
            "matched_skills": matched,
            "missing_skills": missing,
        })

    results.sort(key=lambda r: r["suitability"], reverse=True)
    return results[: Config.TOP_JOB_MATCHES]


def _skill_gap(skills_found, target_role, job_matches):
    found_set = set(skills_found)
    if target_role:
        # aggregate required skills across all job rows for that role title
        mask = store.jobs["title"].str.contains(re.escape(target_role),
                                                case=False, na=False)
        required = set()
        for rs in store.jobs[mask]["skills"]:
            for s in str(rs).split(";"):
                if s.strip():
                    required.add(s.strip())
        role_label = target_role
    elif job_matches:
        required = set(job_matches[0]["matched_skills"] + job_matches[0]["missing_skills"])
        role_label = job_matches[0]["job_title"]
    else:
        return {"target_role": None, "have": [], "missing": []}

    have = sorted(s for s in required if s.lower() in found_set)
    missing = sorted(s for s in required if s.lower() not in found_set)
    return {"target_role": role_label, "have": have, "missing": missing}


def _score(text, word_count, skills_found, sections, experience_years,
           action_verb_count, job_matches):
    # Skills: scaled against a target of ~12 relevant skills
    skills_score = min(100, round(len(skills_found) / 12 * 100))

    # Sections: fraction of the 7 expected sections present
    sections_score = round(len(sections) / len(SECTION_KEYWORDS) * 100)

    # Experience: 0y->40, 8y+->100
    experience_score = min(100, 40 + experience_years * 7) if experience_years else 40

    # Readability: reward a resume in the 300-800 word sweet spot
    if word_count == 0:
        readability = 0
    elif word_count < 150:
        readability = 45
    elif word_count < 300:
        readability = 70
    elif word_count <= 800:
        readability = 100
    elif word_count <= 1200:
        readability = 80
    else:
        readability = 60
    # small bonus for using strong action verbs
    readability = min(100, readability + min(15, action_verb_count * 3))

    # Keyword match: best job similarity, rescaled (cosine rarely exceeds ~0.5)
    best_sim = job_matches[0]["similarity"] if job_matches else 0
    keyword_match = min(100, round(best_sim * 2))

    return {
        "skills": skills_score,
        "sections": sections_score,
        "experience": experience_score,
        "readability": readability,
        "keyword_match": keyword_match,
    }


def _suggestions(sections, skills_found, word_count, action_verb_count,
                 contact, skill_gap, breakdown):
    tips = []
    for section in ("contact", "summary", "experience", "education", "skills"):
        if section not in sections:
            tips.append(f"Add a clear '{section.capitalize()}' section — it appears to be missing.")
    if not contact["email"]:
        tips.append("No email address detected. Add professional contact details near the top.")
    if word_count < 300:
        tips.append("Your resume looks short. Aim for 400-800 words with concrete achievements.")
    elif word_count > 1000:
        tips.append("Your resume is quite long. Tighten it toward one to two focused pages.")
    if action_verb_count < 5:
        tips.append("Use more strong action verbs (led, built, improved, delivered) to describe impact.")
    if "projects" not in sections:
        tips.append("Consider adding a 'Projects' section to showcase applied experience.")
    missing = skill_gap.get("missing", [])[:6]
    if missing:
        tips.append("For your target role, consider adding these in-demand skills: "
                    + ", ".join(missing) + ".")
    if not re.search(r"\d", " ".join(skills_found)) and breakdown["keyword_match"] < 60:
        tips.append("Quantify results with numbers (e.g. 'reduced load time by 40%').")
    if not tips:
        tips.append("Great job! Your resume covers the key sections and matches strong roles.")
    return tips


def _top_demand_skills(skills_found):
    scored = [
        {"skill": store.skill_canonical.get(s, s), "demand": store.skill_demand.get(s, 60)}
        for s in skills_found
    ]
    scored.sort(key=lambda x: x["demand"], reverse=True)
    return scored[:8]
