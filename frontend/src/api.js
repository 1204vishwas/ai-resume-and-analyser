// Centralized API client for the backend.
const BASE = process.env.REACT_APP_API_URL || "/api";

async function handle(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data;
}

export function getStats() {
  return fetch(`${BASE}/stats`).then(handle);
}

export function getRoles() {
  return fetch(`${BASE}/roles`).then(handle);
}

export function analyzeText(text, targetRole) {
  return fetch(`${BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, target_role: targetRole || null }),
  }).then(handle);
}

export function analyzeFile(file, targetRole) {
  const form = new FormData();
  form.append("resume", file);
  if (targetRole) form.append("target_role", targetRole);
  return fetch(`${BASE}/analyze`, { method: "POST", body: form }).then(handle);
}

// ---------- Auth ----------
export function registerUser(name, email, password) {
  return fetch(`${BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  }).then(handle);
}

export function loginUser(email, password) {
  return fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  }).then(handle);
}
