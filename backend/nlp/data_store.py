"""Loads the datasets once and exposes derived NLP resources.

All datasets share the same 5 columns:  title, category, skills, level, description
Built at import time (singleton) so the TF-IDF model over the job-role
corpus is fitted only once and reused for every request.
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from config import Config


class DataStore:
    def __init__(self):
        self.jobs = pd.read_csv(Config.JOB_ROLES_CSV).fillna("")
        self.skills = pd.read_csv(Config.SKILLS_CSV).fillna("")
        self.resumes = pd.read_csv(Config.RESUME_SAMPLES_CSV).fillna("")

        # Pre-split the job "skills" column (semicolon-separated) once.
        self.job_required = [
            [s.strip() for s in str(sk).split(";") if s.strip()]
            for sk in self.jobs["skills"]
        ]

        # --- Skill vocabulary + frequency-based demand ----------------------
        self.skill_canonical = {}   # lower -> display name
        skill_counts = {}           # lower -> occurrences across job postings

        for required in self.job_required:
            for name in required:
                key = name.lower()
                self.skill_canonical.setdefault(key, name)
                skill_counts[key] = skill_counts.get(key, 0) + 1

        # Fold in skill names that only appear in skills.csv (its `title` column)
        for name in self.skills["title"]:
            name = str(name).strip()
            if name:
                self.skill_canonical.setdefault(name.lower(), name)

        # Demand score 50-100, scaled by how often a skill is requested.
        max_count = max(skill_counts.values()) if skill_counts else 1
        self.skill_demand = {
            key: round(50 + 50 * (skill_counts.get(key, 0) / max_count))
            for key in self.skill_canonical
        }

        # skill -> set of related roles (skills.csv `skills` column holds the role)
        self.skill_roles = {}
        for _, row in self.skills.iterrows():
            key = str(row["title"]).strip().lower()
            role = str(row["skills"]).strip()
            if key and role:
                self.skill_roles.setdefault(key, set()).add(role)

        # --- TF-IDF over the job corpus -------------------------------------
        self.job_corpus = (
            self.jobs["title"] + ". "
            + self.jobs["skills"].str.replace(";", " ", regex=False) + ". "
            + self.jobs["description"]
        ).tolist()

        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2),
                                          max_features=8000)
        self.job_matrix = self.vectorizer.fit_transform(self.job_corpus)

    # -- convenience ---------------------------------------------------------
    def categories(self):
        return sorted(self.jobs["category"].unique().tolist())

    def roles(self):
        # The skills dataset's `skills` column holds the associated base role.
        return sorted({r for r in self.skills["skills"].unique().tolist() if r})

    def stats(self):
        return {
            "job_roles": int(len(self.jobs)),
            "skills": int(len(self.skills)),
            "resume_samples": int(len(self.resumes)),
            "unique_skills": int(len(self.skill_canonical)),
            "categories": int(self.jobs["category"].nunique()),
        }


# Singleton instance
store = DataStore()
