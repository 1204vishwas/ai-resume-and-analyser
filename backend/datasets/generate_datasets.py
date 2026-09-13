"""
Dataset generator for the AI Resume Analyzer.

Produces three CSV datasets that ALL share the SAME 5 column names:

    title, category, skills, level, description

Each dataset has between 1000 and 1500 rows.

  1. job_roles.csv      -> one row per job posting
  2. skills.csv         -> one row per skill/role association
  3. resume_samples.csv -> one row per synthetic candidate profile

Run:  python generate_datasets.py
"""

import csv
import os
import random

random.seed(42)  # deterministic / reproducible output

HERE = os.path.dirname(os.path.abspath(__file__))

# Unified column names shared by every dataset in this project.
FIELDNAMES = ["title", "category", "skills", "level", "description"]

# --------------------------------------------------------------------------
# Shared vocabulary
# --------------------------------------------------------------------------

# category -> list of base role titles
ROLES_BY_CATEGORY = {
    "Software Engineering": [
        "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "Mobile Developer", "DevOps Engineer", "QA Engineer",
        "Software Architect", "Game Developer", "Site Reliability Engineer",
    ],
    "Data & AI": [
        "Data Scientist", "Data Analyst", "Data Engineer",
        "Machine Learning Engineer", "NLP Engineer", "Computer Vision Engineer",
        "Business Intelligence Analyst", "AI Researcher",
    ],
    "Design": [
        "UI Designer", "UX Designer", "Product Designer",
        "Graphic Designer", "Interaction Designer",
    ],
    "Product & Management": [
        "Product Manager", "Project Manager", "Scrum Master",
        "Program Manager", "Product Owner",
    ],
    "Marketing": [
        "Digital Marketing Specialist", "SEO Specialist",
        "Content Strategist", "Social Media Manager", "Growth Marketer",
    ],
    "Cloud & Infrastructure": [
        "Cloud Architect", "Cloud Engineer", "Network Engineer",
        "Security Engineer", "Database Administrator",
    ],
    "Business": [
        "Business Analyst", "Financial Analyst", "Operations Manager",
        "HR Specialist", "Sales Engineer",
    ],
}

# role -> list of typical skills
SKILLS_BY_ROLE = {
    "Frontend Developer": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "Redux", "Webpack", "Sass", "Jest", "Accessibility"],
    "Backend Developer": ["Python", "Java", "Node.js", "SQL", "REST APIs", "Django", "Spring Boot", "Redis", "Microservices", "GraphQL"],
    "Full Stack Developer": ["JavaScript", "React", "Node.js", "Python", "SQL", "MongoDB", "Docker", "REST APIs", "Git", "TypeScript"],
    "Mobile Developer": ["Kotlin", "Swift", "Flutter", "React Native", "Android SDK", "iOS", "Firebase", "REST APIs", "Git", "UI Design"],
    "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Jenkins", "Ansible", "Linux", "Bash", "Monitoring"],
    "QA Engineer": ["Selenium", "Test Automation", "Cypress", "JUnit", "Manual Testing", "Postman", "Jira", "Python", "CI/CD", "Bug Tracking"],
    "Software Architect": ["System Design", "Microservices", "Java", "Design Patterns", "AWS", "Kafka", "REST APIs", "Scalability", "Docker", "Leadership"],
    "Game Developer": ["Unity", "C#", "C++", "Unreal Engine", "3D Math", "Physics", "Shaders", "Game Design", "OpenGL", "Optimization"],
    "Site Reliability Engineer": ["Kubernetes", "Prometheus", "Grafana", "Linux", "Python", "Terraform", "Incident Response", "AWS", "Go", "Monitoring"],
    "Data Scientist": ["Python", "Pandas", "NumPy", "Scikit-learn", "Machine Learning", "Statistics", "SQL", "TensorFlow", "Data Visualization", "Jupyter"],
    "Data Analyst": ["SQL", "Excel", "Tableau", "Power BI", "Python", "Statistics", "Data Cleaning", "Pandas", "Reporting", "A/B Testing"],
    "Data Engineer": ["Python", "SQL", "Spark", "Airflow", "Kafka", "ETL", "AWS", "Snowflake", "Data Modeling", "Hadoop"],
    "Machine Learning Engineer": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "MLOps", "Docker", "Machine Learning", "Deep Learning", "SQL", "Model Deployment"],
    "NLP Engineer": ["Python", "NLP", "spaCy", "Transformers", "PyTorch", "Machine Learning", "Text Mining", "BERT", "Deep Learning", "Tokenization"],
    "Computer Vision Engineer": ["Python", "OpenCV", "PyTorch", "Deep Learning", "CNN", "Image Processing", "TensorFlow", "Machine Learning", "C++", "CUDA"],
    "Business Intelligence Analyst": ["SQL", "Power BI", "Tableau", "Data Warehousing", "DAX", "ETL", "Excel", "Reporting", "Python", "Dashboards"],
    "AI Researcher": ["Python", "Deep Learning", "PyTorch", "Research", "Mathematics", "Machine Learning", "TensorFlow", "NLP", "Reinforcement Learning", "Publications"],
    "UI Designer": ["Figma", "Sketch", "Adobe XD", "Prototyping", "Typography", "Color Theory", "Design Systems", "HTML", "CSS", "Wireframing"],
    "UX Designer": ["User Research", "Wireframing", "Figma", "Prototyping", "Usability Testing", "Information Architecture", "Personas", "Journey Mapping", "Design Thinking", "Accessibility"],
    "Product Designer": ["Figma", "User Research", "Prototyping", "Design Systems", "Interaction Design", "Wireframing", "Usability Testing", "Sketch", "UI Design", "UX Design"],
    "Graphic Designer": ["Photoshop", "Illustrator", "InDesign", "Typography", "Branding", "Layout Design", "Color Theory", "Adobe XD", "Creativity", "Print Design"],
    "Interaction Designer": ["Figma", "Prototyping", "Motion Design", "Interaction Design", "User Research", "Wireframing", "Design Systems", "Usability Testing", "After Effects", "UX Design"],
    "Product Manager": ["Roadmapping", "Agile", "Stakeholder Management", "User Stories", "Market Research", "Analytics", "Prioritization", "Jira", "Communication", "Strategy"],
    "Project Manager": ["Agile", "Scrum", "Risk Management", "Budgeting", "Stakeholder Management", "Jira", "Planning", "Communication", "Gantt Charts", "Leadership"],
    "Scrum Master": ["Scrum", "Agile", "Facilitation", "Jira", "Coaching", "Kanban", "Sprint Planning", "Retrospectives", "Communication", "Servant Leadership"],
    "Program Manager": ["Program Management", "Stakeholder Management", "Roadmapping", "Risk Management", "Budgeting", "Agile", "Communication", "Strategy", "Reporting", "Leadership"],
    "Product Owner": ["Backlog Management", "User Stories", "Agile", "Prioritization", "Stakeholder Management", "Scrum", "Roadmapping", "Analytics", "Communication", "Jira"],
    "Digital Marketing Specialist": ["SEO", "Google Ads", "Content Marketing", "Email Marketing", "Analytics", "Social Media", "Campaign Management", "Copywriting", "CRM", "A/B Testing"],
    "SEO Specialist": ["SEO", "Keyword Research", "Google Analytics", "Link Building", "Content Strategy", "Technical SEO", "SEMrush", "On-page SEO", "Copywriting", "HTML"],
    "Content Strategist": ["Content Marketing", "Copywriting", "SEO", "Editorial Planning", "Storytelling", "Analytics", "CMS", "Brand Voice", "Research", "Social Media"],
    "Social Media Manager": ["Social Media", "Content Creation", "Analytics", "Community Management", "Copywriting", "Campaign Management", "Canva", "Scheduling Tools", "Branding", "Engagement"],
    "Growth Marketer": ["Growth Hacking", "A/B Testing", "Analytics", "SEO", "Paid Ads", "Funnel Optimization", "Email Marketing", "SQL", "Experimentation", "CRM"],
    "Cloud Architect": ["AWS", "Azure", "GCP", "System Design", "Terraform", "Kubernetes", "Networking", "Security", "Microservices", "Cost Optimization"],
    "Cloud Engineer": ["AWS", "Terraform", "Docker", "Kubernetes", "Linux", "CI/CD", "Python", "Networking", "CloudFormation", "Monitoring"],
    "Network Engineer": ["Networking", "TCP/IP", "Cisco", "Firewalls", "VPN", "Routing", "Switching", "Linux", "DNS", "Security"],
    "Security Engineer": ["Cybersecurity", "Penetration Testing", "SIEM", "Firewalls", "Encryption", "Linux", "Python", "Incident Response", "OWASP", "Network Security"],
    "Database Administrator": ["SQL", "PostgreSQL", "MySQL", "Oracle", "Backup & Recovery", "Performance Tuning", "Replication", "MongoDB", "Linux", "Security"],
    "Business Analyst": ["Requirements Gathering", "SQL", "Excel", "Process Modeling", "Stakeholder Management", "Documentation", "Agile", "Data Analysis", "UML", "Communication"],
    "Financial Analyst": ["Financial Modeling", "Excel", "Accounting", "Forecasting", "Valuation", "SQL", "Budgeting", "Power BI", "Reporting", "Analytics"],
    "Operations Manager": ["Operations Management", "Process Improvement", "Supply Chain", "Budgeting", "Leadership", "Analytics", "Lean", "Six Sigma", "Vendor Management", "Communication"],
    "HR Specialist": ["Recruitment", "Onboarding", "Employee Relations", "HRIS", "Payroll", "Compliance", "Communication", "Performance Management", "Training", "Conflict Resolution"],
    "Sales Engineer": ["Technical Sales", "CRM", "Product Demos", "Communication", "Negotiation", "Solution Design", "Presentations", "Customer Success", "APIs", "Cloud"],
}

SENIORITY = ["Intern", "Junior", "Mid-level", "Senior", "Lead", "Principal"]
DOMAINS = ["Fintech", "Healthcare", "E-commerce", "SaaS", "Gaming", "EdTech", "Enterprise", "Startup"]
PROFICIENCY = ["Beginner", "Intermediate", "Advanced", "Expert"]
EDUCATION = ["High School", "Associate Degree", "Bachelor's Degree", "Master's Degree", "PhD"]

EXPERIENCE_BY_SENIORITY = {
    "Intern": (0, 1), "Junior": (1, 3), "Mid-level": (3, 6),
    "Senior": (6, 10), "Lead": (8, 14), "Principal": (12, 20),
}

# role -> category (reverse lookup)
ROLE_TO_CATEGORY = {
    role: cat for cat, roles in ROLES_BY_CATEGORY.items() for role in roles
}


def all_roles():
    for cat, roles in ROLES_BY_CATEGORY.items():
        for role in roles:
            yield cat, role


# --------------------------------------------------------------------------
# 1. job_roles.csv
# --------------------------------------------------------------------------
def build_job_roles(target_min=1000, target_max=1500):
    rows = []
    combos = []
    for cat, role in all_roles():
        for level in SENIORITY:
            for domain in DOMAINS:
                combos.append((cat, role, level, domain))
    random.shuffle(combos)

    for cat, role, level, domain in combos:
        if len(rows) >= target_max:
            break
        skills = SKILLS_BY_ROLE.get(role, [])
        n = min(len(skills), random.randint(5, 7))
        required = random.sample(skills, n) if skills else []
        lo, hi = EXPERIENCE_BY_SENIORITY[level]
        title = f"{level} {role}"
        description = (
            f"We are seeking a {title} to join our {domain} team. "
            f"The ideal candidate has {lo}-{hi} years of experience and is proficient in "
            f"{', '.join(required)}. Responsibilities include collaborating with "
            f"cross-functional teams, delivering high-quality work, and driving {cat.lower()} initiatives."
        )
        rows.append({
            "title": title,
            "category": cat,
            "skills": "; ".join(required),
            "level": level,
            "description": description,
        })
    return rows


# --------------------------------------------------------------------------
# 2. skills.csv  (skill -> role association mapping)
# --------------------------------------------------------------------------
def build_skills(target_min=1000, target_max=1500):
    rows = []
    seen = set()
    skill_category = {}
    for cat, role in all_roles():
        for skill in SKILLS_BY_ROLE.get(role, []):
            skill_category.setdefault(skill, cat)

    combos = []
    for skill, cat in skill_category.items():
        for role in ROLES_BY_CATEGORY[cat]:
            combos.append((skill, cat, role))
        for other_cat, role in all_roles():
            if skill in SKILLS_BY_ROLE.get(role, []):
                combos.append((skill, cat, role))
    random.shuffle(combos)

    for skill, cat, role in combos:
        if len(rows) >= target_max:
            break
        key = (skill, role)
        if key in seen:
            continue
        seen.add(key)
        proficiency = random.choice(PROFICIENCY)
        description = (
            f"{skill} is an {proficiency.lower()}-level skill commonly required for "
            f"{role} roles in the {cat} field."
        )
        rows.append({
            "title": skill,
            "category": cat,
            "skills": role,          # the role this skill is associated with
            "level": proficiency,
            "description": description,
        })
    return rows


# --------------------------------------------------------------------------
# 3. resume_samples.csv  (synthetic candidate profiles)
# --------------------------------------------------------------------------
FIRST_SUMMARY = [
    "Results-driven", "Detail-oriented", "Passionate", "Motivated",
    "Experienced", "Innovative", "Dedicated", "Collaborative",
]


def build_resume_samples(target_min=1000, target_max=1500):
    rows = []
    roles = list(SKILLS_BY_ROLE.keys())
    while len(rows) < target_min or (len(rows) < target_max and random.random() < 0.5):
        if len(rows) >= target_max:
            break
        role = random.choice(roles)
        level = random.choice(SENIORITY)
        skills_pool = SKILLS_BY_ROLE[role]
        n = min(len(skills_pool), random.randint(4, 8))
        skills = random.sample(skills_pool, n)
        lo, hi = EXPERIENCE_BY_SENIORITY[level]
        years = random.randint(lo, max(lo, hi))
        edu = random.choice(EDUCATION)
        summary = (
            f"{random.choice(FIRST_SUMMARY)} {role} with {years} years of experience "
            f"skilled in {', '.join(skills[:3])}. Holds a {edu}. "
            f"Seeking to leverage expertise to deliver impact."
        )
        rows.append({
            "title": f"{level} {role}",
            "category": ROLE_TO_CATEGORY.get(role, "General"),
            "skills": "; ".join(skills),
            "level": edu,
            "description": summary,
        })
    return rows


# --------------------------------------------------------------------------
# Writer
# --------------------------------------------------------------------------
def write_csv(filename, rows):
    path = os.path.join(HERE, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {filename:22s} -> {len(rows):5d} rows, {len(FIELDNAMES)} columns")


def main():
    print("Generating datasets (shared columns: %s; 1000-1500 rows each):" % ", ".join(FIELDNAMES))
    write_csv("job_roles.csv", build_job_roles())
    write_csv("skills.csv", build_skills())
    write_csv("resume_samples.csv", build_resume_samples())
    print("Done.")


if __name__ == "__main__":
    main()
