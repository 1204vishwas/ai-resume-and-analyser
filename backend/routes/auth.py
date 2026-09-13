"""Authentication endpoints: register, login, current-user."""
import re

from flask import Blueprint, jsonify, request

from auth import store

auth_api = Blueprint("auth_api", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate(name, email, password):
    if not name or len(name.strip()) < 2:
        return "Please enter your name (at least 2 characters)."
    if not email or not EMAIL_RE.match(email.strip()):
        return "Please enter a valid email address."
    if not password or len(password) < 6:
        return "Password must be at least 6 characters long."
    return None


@auth_api.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")

    err = _validate(name, email, password)
    if err:
        return jsonify({"error": err}), 400

    try:
        user = store.create_user(name, email, password)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409

    token = store.make_token(user)
    return jsonify({"user": user, "token": token}), 201


@auth_api.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = store.authenticate(email, password)
    if not user:
        return jsonify({"error": "Invalid email or password."}), 401

    token = store.make_token(user)
    return jsonify({"user": user, "token": token})


@auth_api.get("/me")
def me():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:] if auth_header.startswith("Bearer ") else ""
    user = store.verify_token(token) if token else None
    if not user:
        return jsonify({"error": "Not authenticated."}), 401
    return jsonify({"user": user})
