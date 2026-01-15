const API_BASE = "http://127.0.0.1:5000";

// ------------------ DOM ------------------

const authSection = document.getElementById("authSection");
const appSection = document.getElementById("appSection");
const authResult = document.getElementById("authResult");
const logoutBtn = document.getElementById("logoutBtn");

// ------------------ Auth ------------------

function register() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
        authResult.innerText = "Username and password required";
        return;
    }

    fetch(`${API_BASE}/api/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            authResult.innerText = data.error;
        } else {
            authResult.innerText = "";
            showApp();
        }
    })
    .catch(() => {
        authResult.innerText = "Server error";
    });
}

function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    fetch(`${API_BASE}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            authResult.innerText = data.error;
        } else {
            authResult.innerText = "";
            showApp();
        }
    })
    .catch(() => {
        authResult.innerText = "Server error";
    });
}

function logout() {
    fetch(`${API_BASE}/api/logout`, {
        method: "POST",
        credentials: "include"
    })
    .finally(() => {
        authSection.style.display = "flex";
        appSection.style.display = "none";
        logoutBtn.style.display = "none";
    });
}

// ------------------ App UI ------------------

function showApp() {
    authSection.style.display = "none";
    appSection.style.display = "flex";
    logoutBtn.style.display = "inline-block";
    loadHistory();
}

// ------------------ Shorten ------------------

function shortenUrl() {
    const input = document.getElementById("urlInput");
    const result = document.getElementById("shortenResult");
    const longUrl = input.value.trim();

    if (!longUrl) {
        result.innerText = "Please enter a URL";
        return;
    }

    fetch(`${API_BASE}/api/shorten`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ long_url: longUrl })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            result.innerText = data.error;
        } else {
            result.innerHTML = `
                Short URL:
                <a href="${data.short_url}" target="_blank">
                    ${data.short_url}
                </a>
            `;
            loadHistory();
        }
    })
    .catch(() => {
        result.innerText = "Server error";
    });
}

// ------------------ History (Cards) ------------------

function loadHistory() {
    fetch(`${API_BASE}/api/urls`, {
        method: "GET",
        credentials: "include"
    })
    .then(res => {
        if (res.status === 401) {
            console.warn("Session not available yet");
            return [];
        }
        return res.json();
    })
    .then(data => {
        const list = document.getElementById("historyList");
        list.innerHTML = "";

        data.forEach(item => {
            const card = document.createElement("div");
            card.className = "history-card";

            card.innerHTML = `
                <div class="history-info">
                    <div class="history-title">${item.link_name}</div>
                    <div class="history-url">
                        <a href="${item.short_url}" target="_blank">
                            ${item.short_url}
                        </a>
                    </div>
                    <div class="history-date">${item.created_at}</div>
                </div>
                <div class="history-delete">
                    <button onclick="deleteLink(${item.id})">🗑️</button>
                </div>
            `;

            list.appendChild(card);
        });
    })
    .catch(err => {
        console.error("History load failed", err);
    });
}

// ------------------ Delete ------------------

function deleteLink(id) {
    if (!confirm("Delete this link?")) return;

    fetch(`${API_BASE}/api/urls/${id}`, {
        method: "DELETE",
        credentials: "include"
    })
    .then(() => loadHistory())
    .catch(() => alert("Delete failed"));
}
