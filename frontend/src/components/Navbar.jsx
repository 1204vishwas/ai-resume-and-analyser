import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const initials = user
    ? user.name.split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase()
    : "";

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <NavLink to="/" className="brand">
          <span className="brand-badge">AI</span>
          <span>Resume Analyzer</span>
        </NavLink>
        <div className="nav-links">
          <NavLink to="/" end className="nav-item nav-collapse">Home</NavLink>
          <NavLink to="/analyze" className="nav-item nav-collapse">Analyze</NavLink>
          <NavLink to="/about" className="nav-item nav-collapse">About</NavLink>

          {user ? (
            <div className="nav-user">
              <span className="avatar" title={user.email}>{initials}</span>
              <span className="nav-username">{user.name.split(" ")[0]}</span>
              <button className="btn btn-ghost" onClick={handleLogout}>Log out</button>
            </div>
          ) : (
            <>
              <NavLink to="/login" className="nav-item">Log in</NavLink>
              <NavLink to="/signup" className="btn btn-primary" style={{ color: "#fff" }}>
                Sign up
              </NavLink>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
