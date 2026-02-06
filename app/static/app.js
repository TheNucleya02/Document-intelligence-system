const API_BASE = "";

function getToken() {
  return localStorage.getItem("access_token");
}

function setTokens(tokens) {
  localStorage.setItem("access_token", tokens.access_token);
  localStorage.setItem("refresh_token", tokens.refresh_token);
}

async function apiFetch(path, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return fetch(`${API_BASE}${path}`, { ...options, headers });
}

function requireAuth() {
  const token = getToken();
  if (!token) {
    window.location.href = "/login";
  }
}

window.App = { apiFetch, setTokens, requireAuth };
