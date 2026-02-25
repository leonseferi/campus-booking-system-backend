const CBS = (() => {
  const TOKEN_KEY = "cbs_token";

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }
  function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
  }
  function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  }

  function esc(s) {
    return String(s ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  async function request(path, { method = "GET", body, auth = true, headers = {} } = {}) {
    const h = { ...headers };

    if (auth) {
      const t = getToken();
      if (!t) throw new Error("Not signed in. Go to /portal/login");
      h["Authorization"] = `Bearer ${t}`;
    }

    if (body !== undefined && !(body instanceof FormData) && !h["Content-Type"]) {
      h["Content-Type"] = "application/json";
    }

    const res = await fetch(path, {
      method,
      headers: h,
      body: body === undefined ? undefined : (body instanceof FormData ? body : JSON.stringify(body)),
    });

    const text = await res.text();
    let data;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }

    if (!res.ok) {
      const msg =
        (data && data.detail && typeof data.detail === "string" && data.detail) ||
        (typeof data === "string" && data) ||
        `${res.status} ${res.statusText}`;
      throw new Error(msg);
    }
    return data;
  }

  function get(path, opts = {}) {
    return request(path, { ...opts, method: "GET" });
  }
  function post(path, body, opts = {}) {
    return request(path, { ...opts, method: "POST", body });
  }

  async function login(email, password) {
    // OAuth2PasswordRequestForm requires x-www-form-urlencoded fields: username, password
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);

    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data?.detail || "Login failed");
    }

    if (!data?.access_token) throw new Error("Login did not return access_token");
    setToken(data.access_token);
    await refreshHeader();
  }

  async function me() {
    return get("/auth/me", { auth: true });
  }

  async function safeMe() {
    try {
      const t = getToken();
      if (!t) return null;
      return await me();
    } catch {
      return null;
    }
  }

  async function refreshHeader() {
    const who = document.getElementById("whoami");
    const btnLogin = document.getElementById("btn-login");
    const btnLogout = document.getElementById("btn-logout");
    const navAdmin = document.getElementById("nav-admin");

    const me = await safeMe();

    if (!who) return;

    if (!me) {
      who.textContent = "Not signed in";
      btnLogin && (btnLogin.style.display = "inline-flex");
      btnLogout && (btnLogout.style.display = "none");
      navAdmin && (navAdmin.style.display = "none");
      return;
    }

    who.textContent = `${me.email} • ${me.role}`;
    btnLogin && (btnLogin.style.display = "none");
    btnLogout && (btnLogout.style.display = "inline-flex");
    navAdmin && (navAdmin.style.display = (me.role === "ADMIN" || me.role === "STAFF") ? "inline-flex" : "none");
  }

  function wireLogout() {
    const btnLogout = document.getElementById("btn-logout");
    if (!btnLogout) return;
    btnLogout.addEventListener("click", () => {
      clearToken();
      refreshHeader();
      window.location.href = "/portal/login";
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    refreshHeader();
    wireLogout();
  });

  return { getToken, setToken, clearToken, esc, request, get, post, login, me, safeMe, refreshHeader };
})();