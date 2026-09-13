"""
Generate SEPARATE job-role datasets per field (developer, AI/ML, etc.).

Each output file keeps the SAME 5-column schema as every other dataset:
    title, category, skills, level, description
and contains between 1000 and 1500 rows.

Output goes to  datasets/by_field/<field>.csv

Run:  python generate_field_datasets.py
"""
import csv
import os
import random

from generate_datasets import (
    DOMAINS,
    EXPERIENCE_BY_SENIORITY,
    ROLES_BY_CATEGORY,
    SENIORITY,
    SKILLS_BY_ROLE,
)

random.seed(7)  # deterministic

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "by_field")

# field file name -> category label used in ROLES_BY_CATEGORY
FIELDS = {
    "developer": "Software Engineering",
    "aiml": "Data & AI",
    "design": "Design",
    "product_management": "Product & Management",
    "marketing": "Marketing",
    "cloud_infrastructure": "Cloud & Infrastructure",
    "business": "Business",
}

WORK_MODE = ["Remote", "Hybrid", "On-site"]
EMP_TYPE = ["Full-time", "Contract", "Internship"]

FIELDNAMES = ["title", "category", "skills", "level", "description"]


def build_field_rows(category, target_min=1000, target_max=1500):
    roles = ROLES_BY_CATEGORY[category]
    combos = []
    for role in roles:
        for level in SENIORITY:
            for domain in DOMAINS:
                for mode in WORK_MODE:
                    for emp in EMP_TYPE:
                        combos.append((role, level, domain, mode, emp))
    random.shuffle(combos)

    rows = []
    for role, level, domain, mode, emp in combos:
        if len(rows) >= target_max:
            break
        skills = SKILLS_BY_ROLE.get(role, [])
        n = min(len(skills), random.randint(5, 7))
        required = random.sample(skills, n) if skills else []
        lo, hi = EXPERIENCE_BY_SENIORITY[level]
        title = f"{level} {role}"
        description = (
            f"{emp} · {mode}. We are hiring a {title} for our {domain} team. "
            f"The ideal candidate has {lo}-{hi} years of experience and is proficient in "
            f"{', '.join(required)}. This is a {mode.lower()} {emp.lower()} position "
            f"focused on delivering high-quality {category.lower()} work."
        )
        rows.append({
            "title": title,
            "category": category,
            "skills": "; ".join(required),
            "level": level,
            "description": description,
        })

    if len(rows) < target_min:
        raise RuntimeError(f"{category}: only {len(rows)} rows (< {target_min}).")
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Generating per-field datasets (5 columns, 1000-1500 rows each) -> {OUT_DIR}")
    for fname, category in FIELDS.items():
        rows = build_field_rows(category)
        path = os.path.join(OUT_DIR, f"{fname}.csv")
        write_csv(path, rows)
        print(f"  {fname + '.csv':28s} -> {len(rows):5d} rows  ({category})")
    print("Done.")


if __name__ == "__main__":
    main()
