# AI Resume Analyzer

An **NLP-powered resume analyzer** with a **React** frontend and a **Python/Flask**
backend. Upload or paste a resume and instantly get:

- an overall **score** (5 weighted dimensions),
- the **best-fit role** with a **suitability %**, plus a ranked list of matching roles,
- **extracted skills** and skills ranked by market demand,
- a **skill-gap** report for your target role,
- **actionable suggestions** to improve the resume.

Everything is computed locally with classic, explainable NLP (TF-IDF + cosine
similarity) — no external LLM API, no data leaves the app. It also ships a
**machine-learning module** that trains and compares several classifiers on the datasets.

## Project structure

```
ai resume and analyser/
├── package.json          Root scripts: `npm start` runs BOTH servers together
├── backend/              Python + Flask + scikit-learn
│   ├── app.py            Flask entry point (REST API)
│   ├── config.py
│   ├── requirements.txt
│   ├── nlp/              extractor · data_store · analyzer
│   ├── ml/              train_models.py (trains + compares ML models)
│   ├── auth/            JSON user store (hashed passwords, signed tokens)
│   ├── routes/          api.py · auth.py  (REST blueprints)
│   └── datasets/        3 CSVs + per-field CSVs + generators
└── frontend/            React 18 + React Router (all files .jsx)
    ├── public/
    └── src/             pages/ · components/ · context/ · api.js
```

## Prerequisites

- **Python 3.11+**  and  **Node.js 18+** (npm 9+)

## Quick start — run both with `npm start`

**First-time setup** (create the Python venv, then install everything):

```bash
cd backend
```
```bash
python -m venv venv
```
```bash
venv\Scripts\python.exe -m pip install -r requirements.txt
```
```bash
cd ..
```
```bash
npm run install:all
```

**Every time after that**, from the project root, one command starts **both** the
Flask backend (`:5000`) and the React frontend (`:3000`):

```bash
npm start
```

Output is labeled `[BACKEND]` / `[FRONTEND]`, and `Ctrl+C` stops both.
Then open **http://localhost:3000**.

> On **Windows** (PowerShell) the backend script uses `venv\Scripts\python.exe`.
> On **macOS/Linux**, change that path in the root `package.json` to `venv/bin/python`.

### Root scripts

| Command | Runs |
|---------|------|
| `npm start` | **both** backend + frontend |
| `npm run start:backend` | just Flask (`:5000`) |
| `npm run start:frontend` | just React (`:3000`) |
| `npm run install:all` | install root + frontend + backend deps |

### Run each separately (two terminals)

```bash
cd backend
venv\Scripts\python.exe app.py
```
```bash
cd frontend
npm start
```

The React dev server proxies API calls to the backend (`"proxy"` in
`frontend/package.json`), so both must run together.

## API endpoints

| Method | Endpoint              | Description                                  |
|--------|-----------------------|----------------------------------------------|
| GET    | `/api/health`         | Health check                                 |
| GET    | `/api/stats`          | Dataset statistics                           |
| GET    | `/api/roles`          | Selectable target roles                      |
| POST   | `/api/analyze`        | Analyze a resume (file upload or JSON text)  |
| POST   | `/api/auth/register`  | Create an account (name, email, password)    |
| POST   | `/api/auth/login`     | Log in, returns a signed token + user        |
| GET    | `/api/auth/me`        | Current user (requires `Authorization` token)|

## Datasets

Every dataset shares the **exact same 5 column names** — `title, category, skills,
level, description` — and each has **1000–1500 rows**. The meaning of each column
adapts to the dataset:

| File                 | Rows  | `title` | `level` |
|----------------------|-------|---------|---------|
| `job_roles.csv`      | 1,500 | job title | experience level |
| `skills.csv`         | 1,500 | skill name | proficiency |
| `resume_samples.csv` | 1,002 | candidate role | education |

Per-field job datasets live in `datasets/by_field/` (developer, aiml, design,
product_management, marketing, cloud_infrastructure, business) — each 1,500 rows
with the **same 5 columns**.

Regenerate them anytime (deterministic, seeded):

```bash
cd backend/datasets
```
```bash
python generate_datasets.py
```
```bash
python generate_field_datasets.py
```

## How the NLP analysis works

1. **Text extraction** — PDF (`pdfplumber`), DOCX (`python-docx`), or plain text.
2. **Tokenization & cleaning** — lowercasing, tokenization, stopword removal.
3. **Skill & section detection** — word-boundary phrase matching against a 240+ skill
   vocabulary; header-keyword matching for resume sections.
4. **Role matching** — TF-IDF + cosine similarity against 1,500 job roles; the best
   posting per role is scored by **suitability** = 60% skill coverage + 40% text
   similarity, surfacing the **best-fit role** and a diverse ranked list.
5. **Scoring & suggestions** — five weighted dimensions (skills, sections, experience,
   readability, keyword match) plus a prioritized list of improvement tips.

## Machine-learning module

`backend/ml/train_models.py` trains and compares **7 classifiers** to predict the job
**role from skills** (TF-IDF features). It saves each model, the best model, a report
(`.csv`/`.md`), and an accuracy chart (`model_comparison.png`).

The file uses `# %%` cell markers, so in **VS Code** you can run it cell-by-cell in the
interactive window, or run the whole script:

```bash
cd backend
venv\Scripts\python.exe ml\train_models.py
```

Latest run: **Logistic Regression** was best at **98.2%** accuracy (2,502 rows, 42 roles).

## Authentication

Responsive **Signup** (`/signup`) and **Login** (`/login`) pages in React, backed by
Flask endpoints. Passwords are hashed with Werkzeug (PBKDF2) and stored in
`backend/data/users.json` — **never in plaintext**. A signed token (itsdangerous) is
issued on login/register and the session is persisted client-side via an `AuthProvider`
context. This file-based store is intended for a demo/learning project; use a real
database in production.

## Tech stack

- **Frontend:** React 18, React Router 6, custom CSS design system (all source files `.jsx`)
- **Backend:** Flask, flask-cors, scikit-learn, pandas, numpy, pdfplumber, python-docx
- **ML/plots:** scikit-learn, matplotlib, joblib
