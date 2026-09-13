"""
Train and compare multiple ML models on the resume/job datasets.

Task: text classification — predict the job `role` from a candidate's `skills`
alone (no title/description leakage), using TF-IDF features.

This file is written with `# %%` cell markers, so in VS Code you can either:
  * Run the whole thing:      python train_models.py
  * Or click "Run Cell" above each `# %%` to run it interactively (with the
    accuracy chart shown inline in VS Code's interactive window).

Outputs (written next to this file):
  models/<model>.joblib        every trained model
  models/tfidf_vectorizer.joblib
  models/best_model.joblib     the highest-accuracy model
  model_report.csv / .md       the comparison table
  model_comparison.png         accuracy bar chart
"""
# %%
# --- Imports & setup -------------------------------------------------------
import json
import os
import time
import warnings

warnings.filterwarnings("ignore")  # keep the training output clean

import joblib
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")  # headless-safe; VS Code interactive still shows plots
import matplotlib.pyplot as plt

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(HERE, "..", "datasets")
MODELS_DIR = os.path.join(HERE, "models")
os.makedirs(MODELS_DIR, exist_ok=True)


# %%
# --- Load & combine datasets ----------------------------------------------
# Task: predict the base ROLE from the SKILLS only (no title/description, so
# the role name never leaks into the features) — a genuine, app-relevant task.
SENIORITY_PREFIXES = ("Intern", "Junior", "Mid-level", "Senior", "Lead", "Principal")


def base_role(title):
    for prefix in SENIORITY_PREFIXES:
        if title.startswith(prefix + " "):
            return title[len(prefix) + 1:]
    return title


def load_data():
    frames = []
    # job_roles + resume_samples both have real skill lists in `skills`.
    for name in ["job_roles.csv", "resume_samples.csv"]:
        df = pd.read_csv(os.path.join(DATASETS_DIR, name)).fillna("")
        frames.append(df)
    data = pd.concat(frames, ignore_index=True)
    data["role"] = data["title"].astype(str).apply(base_role)
    # Feature text = skills ONLY (semicolons -> spaces)
    data["text"] = data["skills"].astype(str).str.replace(";", " ", regex=False)
    data = data[data["text"].str.strip().str.len() > 0]
    # keep roles with enough samples for a stratified split
    counts = data["role"].value_counts()
    data = data[data["role"].isin(counts[counts >= 5].index)]
    return data


data = load_data()
print(f"Loaded {len(data)} rows across {data['role'].nunique()} job roles.")
print("Predicting ROLE from SKILLS. Top roles by sample count:")
print(data["role"].value_counts().head(10).to_string())


# %%
# --- Vectorize (TF-IDF) & train/test split ---------------------------------
X_text = data["text"].tolist()
y = data["role"].tolist()

vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=3000)
X = vectorizer.fit_transform(X_text)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"TF-IDF matrix: {X.shape}  |  train={X_train.shape[0]}  test={X_test.shape[0]}")


# %%
# --- Define all the models -------------------------------------------------
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Multinomial Naive Bayes": MultinomialNB(),
    "Linear SVM": LinearSVC(),
    "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=7),
}


# %%
# --- Train, evaluate, and save every model ---------------------------------
results = []
for name, model in models.items():
    t0 = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - t0

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds, average="macro")

    fname = name.lower().replace(" ", "_") + ".joblib"
    joblib.dump(model, os.path.join(MODELS_DIR, fname))

    results.append({
        "model": name,
        "accuracy": round(acc, 4),
        "macro_f1": round(f1, 4),
        "train_time_s": round(train_time, 3),
        "file": fname,
    })
    print(f"  {name:26s} acc={acc:.4f}  f1={f1:.4f}  ({train_time:.2f}s)")

report = pd.DataFrame(results).sort_values("accuracy", ascending=False).reset_index(drop=True)


# %%
# --- Save vectorizer + best model + reports --------------------------------
joblib.dump(vectorizer, os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib"))

best_row = report.iloc[0]
best_model = joblib.load(os.path.join(MODELS_DIR, best_row["file"]))
joblib.dump(best_model, os.path.join(MODELS_DIR, "best_model.joblib"))

report.to_csv(os.path.join(HERE, "model_report.csv"), index=False)
with open(os.path.join(HERE, "model_report.md"), "w", encoding="utf-8") as f:
    f.write("# Model comparison — predict job role from skills\n\n")
    f.write(f"- Rows: **{len(data)}**  |  Roles (classes): **{data['role'].nunique()}**  "
            f"|  Features: TF-IDF over skills (max 3000, 1-2 grams)\n")
    f.write(f"- Best model: **{best_row['model']}** "
            f"(accuracy {best_row['accuracy']:.4f}, macro-F1 {best_row['macro_f1']:.4f})\n\n")
    f.write(report.to_markdown(index=False))
    f.write("\n")

print("\n=== RANKING (best first) ===")
print(report.to_string(index=False))
print(f"\nBest model: {best_row['model']} ({best_row['accuracy']:.2%} accuracy) -> models/best_model.joblib")


# %%
# --- Plot accuracy comparison ----------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(report)))
bars = ax.barh(report["model"][::-1], report["accuracy"][::-1], color=colors)
ax.set_xlabel("Accuracy")
ax.set_xlim(0, 1.0)
ax.set_title("Model comparison — predict job role from skills")
for bar, val in zip(bars, report["accuracy"][::-1]):
    ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2, f"{val:.3f}",
            va="center", fontsize=9)
plt.tight_layout()
chart_path = os.path.join(HERE, "model_comparison.png")
plt.savefig(chart_path, dpi=120)
print(f"Saved chart -> {chart_path}")
plt.show()


# %%
# --- Quick demo: predict a category from free text -------------------------
def predict_category(text):
    vec = vectorizer.transform([text])
    return best_model.predict(vec)[0]


if __name__ == "__main__":
    demo = "Experienced data scientist skilled in Python, machine learning, TensorFlow and SQL."
    print(f"\nDemo prediction:\n  '{demo}'\n  -> {predict_category(demo)}")
