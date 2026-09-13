import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { loginUser, registerUser } from "../api";

const AuthContext = createContext(null);
const STORAGE_KEY = "ra_auth";

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(null); // { user, token }

  // Restore session on first load
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) setAuth(JSON.parse(saved));
    } catch {
      /* ignore corrupt/blocked storage */
    }
  }, []);

  const persist = useCallback((data) => {
    setAuth(data);
    try {
      if (data) localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      else localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* storage may be unavailable */
    }
  }, []);

  const signup = useCallback(async (name, email, password) => {
    const data = await registerUser(name, email, password);
    persist(data);
    return data;
  }, [persist]);

  const login = useCallback(async (email, password) => {
    const data = await loginUser(email, password);
    persist(data);
    return data;
  }, [persist]);

  const logout = useCallback(() => persist(null), [persist]);

  const value = useMemo(
    () => ({ user: auth?.user || null, token: auth?.token || null, signup, login, logout }),
    [auth, signup, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
