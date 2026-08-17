// frontend/auth.js

const API_BASE = "";

/**
 * Returns the currently authenticated user.
 * Returns null if the user is not logged in.
 */
async function getCurrentUser() {

    try {

        const response = await fetch(`${API_BASE}/auth/me`, {
            method: "GET",
            credentials: "include",
        });

        if (!response.ok) {
            return null;
        }

        const data = await response.json();

        if (!data.authenticated) {
            return null;
        }

        return data.user;

    } catch (error) {

        console.error("Failed to get current user:", error);
        return null;
    }
}


/**
 * Checks authentication when the chat page loads.
 * Redirects back to login page if no session exists.
 */
async function initializeAuthentication() {

    const user = await getCurrentUser();

    if (!user) {

        window.location.href = "/";
        return;
    }

    const userInfo = document.getElementById("user-info");

    if (userInfo) {
        userInfo.textContent = `${user.name} (${user.email})`;
    }
}


/**
 * Starts Microsoft login.
 */
function login() {

    window.location.href = `${API_BASE}/auth/login`;
}


/**
 * Logs the user out.
 */
function logout() {

    window.location.href = `${API_BASE}/auth/logout`;
}


/**
 * Redirects to the chat page after successful login.
 */
function openChat() {

    window.location.href = "/chat.html";
}