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

// Overlay elements
const profileOverlay = document.getElementById("profileOverlay");
const profileUsername = document.getElementById("profileUsername");
const profileLinks = document.getElementById("profileLinks");
const profileClicks = document.getElementById("profileClicks");

// Custom input elements
const customInputWrapper = document.getElementById("customInputWrapper");
const customBtn = document.getElementById("customBtn");
const generateBtn = document.getElementById("generateBtn");
const customInput = document.getElementById("customCodeInput");

// ------------------ Helper Functions ------------------

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

function hideAuthResult() {
    authResult.classList.remove('visible');
    authResult.textContent = '';
}

function initPasswordToggle() {
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.innerHTML = '<i class="fas fa-eye"></i>';
        
        togglePasswordBtn.addEventListener("click", () => {
            const isPassword = passwordInput.type === "password";
            passwordInput.type = isPassword ? "text" : "password";
            togglePasswordBtn.innerHTML = isPassword 
                ? '<i class="fas fa-eye-slash"></i>' 
                : '<i class="fas fa-eye"></i>';
        });
    }
}

// ------------------ Custom Input Functions ------------------

function toggleCustomInput() {
    if (customInputWrapper.style.display === "none" || customInputWrapper.style.display === "") {
        // Show custom input, hide custom button
        customInputWrapper.style.display = "flex";
        customBtn.style.display = "none";
        
        // Make generate button 90% width
        generateBtn.style.width = "90%";
        
        // Focus on the input
        customInput.focus();
    }
}

function closeCustomInput() {
    customInputWrapper.style.display = "none";
    customBtn.style.display = "block";
    
    // Reset generate button to full width
    generateBtn.style.width = "";
    
    // Clear the input
    customInput.value = "";
}

// ------------------ Initialization ------------------

document.addEventListener('DOMContentLoaded', function() {
    initPasswordToggle();
    checkAuthStatus();
    
    // Make sure custom input is hidden initially
    if (customInputWrapper) {
        customInputWrapper.style.display = "none";
    }
    
    const usernameInput = document.getElementById("username");
    if (usernameInput) {
        usernameInput.addEventListener("input", hideAuthResult);
    }
    
    if (passwordInput) {
        passwordInput.addEventListener("input", hideAuthResult);
    }
    
    const urlInput = document.getElementById("urlInput");
    if (urlInput) {
        urlInput.addEventListener("input", function() {
            shortenResult.classList.remove("visible");
            shortenResult.textContent = '';
        });
        
        // Enter key support for main URL input
        urlInput.addEventListener("keydown", function(e) {
            if (e.key === "Enter") {
                e.preventDefault();
                shortenUrl();
            }
        });
    }
    
    // Enter key support for custom code input
    if (customInput) {
        customInput.addEventListener("keydown", function(e) {
            if (e.key === "Enter") {
                e.preventDefault();
                shortenUrl();
            }
        });
    }
});

if (authForm) {
    authForm.addEventListener("submit", (e) => {
        e.preventDefault();
        login();
    });
}

// ------------------ Auth Functions ------------------

function checkAuthStatus() {
    fetch(`${API_BASE}/api/check-auth`, {
        method: "GET",
        credentials: "include"
    })
    .then(res => res.json())
    .then(data => {
        if (data.authenticated) {
            showApp();
        }
    })
    .catch(() => {
        authSection.style.display = "flex";
        appSection.style.display = "none";
        logoutBtn.style.display = "none";
        hideAuthResult();
    });
}

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
    .then(res => {
        if (res.status === 401) {
            return res.json().then(data => {
                if (confirm("User not found. Would you like to register a new account?")) {
                    register();
                }
                return null;
            });
        }
        return res.json();
    })
    .then(data => {
        if (data && data.error) {
            showAuthResult(data.error);
        } else if (data && data.message) {
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

// ------------------ Profile Overlay ------------------

function openProfile() {
    fetch(`${API_BASE}/api/stats`, {
        method: "GET",
        credentials: "include"
    })
    .then(res => res.json())
    .then(data => {
        profileUsername.textContent = data.username;
        profileLinks.textContent = data.total_links;
        profileClicks.textContent = data.total_clicks;
        profileOverlay.style.display = "flex";
    })
    .catch(() => {
        alert("Failed to load profile stats");
    });
}

function closeProfile(event) {
    if (!event || event.target.id === "profileOverlay") {
        profileOverlay.style.display = "none";
    }
}

// ------------------ Shorten ------------------

function shortenUrl() {
    const longUrl = document.getElementById("urlInput").value.trim();
    const customCode = document.getElementById("customCodeInput").value.trim();
    const result = document.getElementById("shortenResult");

    if (!longUrl) {
        result.textContent = "Please enter a URL";
        result.className = "result visible warning";
        return;
    }

    fetch(`${API_BASE}/api/shorten`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ 
            long_url: longUrl,
            custom_code: customCode || null
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            result.textContent = data.error;
            result.className = "result visible error";
        } else {
            result.innerHTML = `
                <span class="result-text">Short URL:</span>
                <a href="${data.short_url}" target="_blank" class="result-link">${data.short_url}</a>
                <div class="result-actions">
                    <button class="action-btn copy-btn" aria-label="Copy URL"><i class="fas fa-copy"></i></button>
                    <button class="action-btn share-btn" aria-label="Share URL"><i class="fas fa-share-alt"></i></button>
                </div>
            `;
            result.className = "result visible success";
            document.getElementById("urlInput").value = "";
            customInput.value = "";
            closeCustomInput(); // Reset custom input state
            loadHistory();
            setupResultActions(result);
        }
    })
    .catch(() => {
        result.textContent = "Server error";
        result.className = "result visible error";
    });
}

function setupResultActions(resultDiv) {
    const copyBtn = resultDiv.querySelector('.copy-btn');
    const shareBtn = resultDiv.querySelector('.share-btn');
    const link = resultDiv.querySelector('.result-link');
    if (!link) return;
    const url = link.href;

    if (copyBtn) {
        copyBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            navigator.clipboard.writeText(url).then(() => {
                alert('URL copied to clipboard!');
            }).catch(() => alert('Copy failed.'));
        });
    }

    if (shareBtn) {
        shareBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            if (navigator.share) {
                navigator.share({
                    title: 'Shared URL',
                    url: url
                }).catch(err => {
                    if (err.name !== 'AbortError') alert('Share failed.');
                });
            } else {
                navigator.clipboard.writeText(url).then(() => {
                    alert('URL copied to clipboard (share not supported).');
                }).catch(() => alert('Copy failed.'));
            }
        });
    }
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
                    <div class="history-date">
                        Created: ${item.created_at}
                        <br>
                        Clicks: ${item.click_count}
                    </div>
                </div>
                <div class="history-delete">
                    <button onclick="deleteLink(${item.id})" aria-label="Delete link">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            list.appendChild(card);
        });
        
        // Setup the option menu after loading history
        setupOptionMenu();
    })
    .catch(err => {
        console.error("History load failed", err);
    });
}

// ------------------ Option Menu (3 Options) ------------------

function setupOptionMenu() {
    // If menu already exists, remove it to avoid duplicates
    const existingMenu = document.querySelector('.option-menu');
    if (existingMenu) existingMenu.remove();

    // Create the floating menu
    const menu = document.createElement('div');
    menu.className = 'option-menu';
    menu.innerHTML = `
        <button class="option-open">Open</button>
        <button class="option-copy">Copy</button>
        <button class="option-share">Share</button>
    `;
    document.body.appendChild(menu);

    // Hide menu initially
    menu.style.display = 'none';

    // Event delegation: listen for clicks on any .history-url
    const historyList = document.getElementById('historyList');
    
    // Remove old listener and add new one
    historyList.removeEventListener('click', historyClickHandler);
    historyList.addEventListener('click', historyClickHandler);

    function historyClickHandler(e) {
        const historyUrlDiv = e.target.closest('.history-url');
        if (!historyUrlDiv) return;

        e.preventDefault();
        e.stopPropagation();

        const anchor = historyUrlDiv.querySelector('a');
        if (!anchor) return;
        const url = anchor.href;

        // Position menu near cursor
        const { clientX, clientY } = e;
        const menuWidth = 150;
        const menuHeight = 130;
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        let left = clientX + 20;
        let top = clientY;

        if (left + menuWidth > viewportWidth) {
            left = clientX - menuWidth - 10;
        }
        if (top + menuHeight > viewportHeight) {
            top = clientY - menuHeight - 10;
        }

        menu.style.left = left + 'px';
        menu.style.top = top + 'px';
        menu.style.display = 'block';
        menu.dataset.url = url;
    }

    // Hide menu when clicking outside
    document.removeEventListener('click', documentClickHandler);
    document.addEventListener('click', documentClickHandler);

    function documentClickHandler(e) {
        if (menu.style.display === 'block' && !menu.contains(e.target)) {
            menu.style.display = 'none';
        }
    }

    // Handle menu option clicks
    menu.removeEventListener('click', menuClickHandler);
    menu.addEventListener('click', menuClickHandler);

    function menuClickHandler(e) {
        e.stopPropagation();
        const target = e.target;
        const url = menu.dataset.url;
        if (!url) return;

        if (target.classList.contains('option-open')) {
            window.open(url, '_blank');
            menu.style.display = 'none';
        }
        else if (target.classList.contains('option-copy')) {
            navigator.clipboard.writeText(url)
                .then(() => {
                    // Show temporary success message
                    const oldContent = menu.innerHTML;
                    menu.innerHTML = '<button style="color: var(--minimal-dark-success);">Copied!</button>';
                    setTimeout(() => {
                        menu.innerHTML = oldContent;
                        menu.style.display = 'none';
                    }, 1000);
                })
                .catch(() => alert('Copy failed.'));
        }
        else if (target.classList.contains('option-share')) {
            if (navigator.share) {
                navigator.share({ title: 'Shared link', url })
                    .catch(err => {
                        if (err.name !== 'AbortError') alert('Share failed.');
                    });
            } else {
                navigator.clipboard.writeText(url)
                    .then(() => {
                        alert('Link copied to clipboard (share not supported).');
                    })
                    .catch(() => alert('Copy failed.'));
            }
            menu.style.display = 'none';
        }
    }
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
