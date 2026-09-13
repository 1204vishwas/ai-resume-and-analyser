"""Application configuration."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
DATA_DIR = os.path.join(BASE_DIR, "data")


class Config:
    # Flask
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    # Auth
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me-in-production")
    TOKEN_MAX_AGE = 60 * 60 * 24 * 7  # 7 days
    USERS_FILE = os.path.join(DATA_DIR, "users.json")

    # Uploads
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

    # NLP
    TOP_JOB_MATCHES = 5

    # Dataset paths
    JOB_ROLES_CSV = os.path.join(DATASETS_DIR, "job_roles.csv")
    SKILLS_CSV = os.path.join(DATASETS_DIR, "skills.csv")
    RESUME_SAMPLES_CSV = os.path.join(DATASETS_DIR, "resume_samples.csv")
