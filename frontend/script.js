const API_BASE = "http://127.0.0.1:5000";

// ------------------ DOM ------------------

const authSection = document.getElementById("authSection");
const appSection = document.getElementById("appSection");
const authResult = document.getElementById("authResult");
const shortenResult = document.getElementById("shortenResult");
const logoutBtn = document.getElementById("logoutBtn");
const authForm = document.getElementById("authForm");
const togglePasswordBtn = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

// ------------------ Helper Functions ------------------

// Show auth result
function showAuthResult(message, isError = true) {
    if (message) {
        authResult.textContent = message;
        authResult.classList.add('visible');
        if (isError) {
            authResult.style.borderLeft = "4px solid var(--minimal-dark-error)";
            authResult.style.background = "rgba(207, 102, 121, 0.1)";
        } else {
            authResult.style.borderLeft = "4px solid var(--minimal-dark-success)";
            authResult.style.background = "rgba(3, 218, 198, 0.1)";
        }
    } else {
        hideAuthResult();
    }
}

// Hide auth result
function hideAuthResult() {
    authResult.classList.remove('visible');
    authResult.textContent = '';
}

// Initialize password toggle
function initPasswordToggle() {
    if (togglePasswordBtn && passwordInput) {
        // Set initial icon
        togglePasswordBtn.innerHTML = '<i class="fas fa-eye"></i>';
        togglePasswordBtn.setAttribute("aria-label", "Show password");
        
        togglePasswordBtn.addEventListener("click", () => {
            const isPassword = passwordInput.type === "password";
            
            if (isPassword) {
                passwordInput.type = "text";
                togglePasswordBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
                togglePasswordBtn.classList.add("active");
                togglePasswordBtn.setAttribute("aria-label", "Hide password");
            } else {
                passwordInput.type = "password";
                togglePasswordBtn.innerHTML = '<i class="fas fa-eye"></i>';
                togglePasswordBtn.classList.remove("active");
                togglePasswordBtn.setAttribute("aria-label", "Show password");
            }
        });
    }
}

// ------------------ Initialization ------------------

// Check if user is already logged in
function checkAuthStatus() {
    fetch(`${API_BASE}/api/check-auth`, {
        method: "GET",
        credentials: "include"
    })
    .then(res => {
        if (res.ok) {
            return res.json();
        }
        throw new Error('Not authenticated');
    })
    .then(data => {
        if (data.authenticated) {
            showApp();
        } else {
            hideAuthResult();
        }
    })
    .catch(() => {
        authSection.style.display = "flex";
        appSection.style.display = "none";
        logoutBtn.style.display = "none";
        hideAuthResult();
    });
}

// ------------------ Event Listeners ------------------

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initPasswordToggle();
    checkAuthStatus();
    
    // Hide auth result when user starts typing
    const usernameInput = document.getElementById("username");
    if (usernameInput) {
        usernameInput.addEventListener("input", hideAuthResult);
    }
    
    if (passwordInput) {
        passwordInput.addEventListener("input", hideAuthResult);
    }
    
    // Hide shorten result when user starts typing
    const urlInput = document.getElementById("urlInput");
    if (urlInput) {
        urlInput.addEventListener("input", function() {
            shortenResult.classList.remove("visible");
            shortenResult.textContent = '';
        });
    }
});

// Submit login on Enter
if (authForm) {
    authForm.addEventListener("submit", (e) => {
        e.preventDefault();
        login();
    });
}

// ------------------ Auth Functions ------------------

function register() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
        showAuthResult("Username and password required");
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
            showAuthResult(data.error);
        } else {
            hideAuthResult();
            showApp();
        }
    })
    .catch(() => {
        showAuthResult("Server error");
    });
}

function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
        showAuthResult("Username and password required");
        return;
    }

    fetch(`${API_BASE}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            showAuthResult(data.error);
        } else {
            hideAuthResult();
            showApp();
        }
    })
    .catch(() => {
        showAuthResult("Server error");
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
        document.getElementById("authForm").reset();
        hideAuthResult();
    });
}

// ------------------ App UI ------------------

function showApp() {
    authSection.style.display = "none";
    appSection.style.display = "flex";
    logoutBtn.style.display = "inline-block";
    loadHistory();
    hideAuthResult();
}

// ------------------ Shorten ------------------

function shortenUrl() {
    const input = document.getElementById("urlInput");
    const result = document.getElementById("shortenResult");
    const longUrl = input.value.trim();

    if (!longUrl) {
        result.textContent = "Please enter a URL";
        result.className = "result visible warning";
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
            result.textContent = data.error;
            result.className = "result visible error";
        } else {
            result.innerHTML = `Short URL: <a href="${data.short_url}" target="_blank">${data.short_url}</a>`;
            result.className = "result visible success";
            input.value = "";
            loadHistory();
        }
    })
    .catch(() => {
        result.textContent = "Server error";
        result.className = "result visible error";
    });
}

// ------------------ History ------------------

function loadHistory() {
    fetch(`${API_BASE}/api/urls`, {
        method: "GET",
        credentials: "include"
    })
    .then(res => {
        if (res.status === 401) return [];
        return res.json();
    })
    .then(data => {
        const list = document.getElementById("historyList");
        list.innerHTML = "";

        if (data.length === 0) {
            list.innerHTML = `
                <div class="history-card" style="text-align: center; color: var(--minimal-dark-text-tertiary);">
                    <i class="fas fa-inbox" style="font-size: 2rem; margin-bottom: 10px; display: block;"></i>
                    No shortened URLs yet. Create your first one above!
                </div>
            `;
            return;
        }

        data.forEach(item => {
            const card = document.createElement("div");
            card.className = "history-card";
            card.innerHTML = `
                <div class="history-info">
                    <div class="history-title">${item.link_name || 'Short Link'}</div>
                    <div class="history-url">
                        <a href="${item.short_url}" target="_blank">${item.short_url}</a>
                    </div>
                    <div class="history-date">${item.created_at}</div>
                </div>
                <div class="history-delete">
                    <button onclick="deleteLink(${item.id})" aria-label="Delete link">
                        <i class="fas fa-trash"></i>
                    </button>
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
    .catch(() => {
        const result = document.getElementById("shortenResult");
        result.textContent = "Failed to delete link";
        result.className = "result visible error";
        setTimeout(() => {
            result.className = "result";
            result.textContent = '';
        }, 3000);
    });
}