"""Simple JSON-file user store with hashed passwords and signed tokens.

Passwords are never stored in plaintext — only Werkzeug PBKDF2 hashes.
Suitable for a demo / learning project. For production, swap the JSON file
for a real database.
"""
import json
import os
import threading
import uuid

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config

_lock = threading.Lock()
_serializer = URLSafeTimedSerializer(Config.SECRET_KEY, salt="auth-token")


def _load():
    if not os.path.exists(Config.USERS_FILE):
        return {}
    try:
        with open(Config.USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(users):
    os.makedirs(os.path.dirname(Config.USERS_FILE), exist_ok=True)
    with open(Config.USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def _public(user):
    """Return only the fields safe to send to the client."""
    return {"id": user["id"], "name": user["name"], "email": user["email"]}


def create_user(name, email, password):
    """Create a user. Raises ValueError if the email already exists."""
    email = email.strip().lower()
    with _lock:
        users = _load()
        if email in users:
            raise ValueError("An account with this email already exists.")
        user = {
            "id": uuid.uuid4().hex,
            "name": name.strip(),
            "email": email,
            "password_hash": generate_password_hash(password),
        }
        users[email] = user
        _save(users)
    return _public(user)


def authenticate(email, password):
    """Return the public user dict on success, else None."""
    email = email.strip().lower()
    users = _load()
    user = users.get(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return None
    return _public(user)


def make_token(user):
    return _serializer.dumps({"id": user["id"], "email": user["email"]})


def verify_token(token):
    """Return the public user for a valid token, else None."""
    try:
        data = _serializer.loads(token, max_age=Config.TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    users = _load()
    user = users.get(data.get("email"))
    return _public(user) if user else None
