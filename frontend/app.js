const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("chat-input");
let history = [];

function timeNow() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function addMessage(role, content, { isTyping = false } = {}) {
  const wrapper = document.createElement("div");
  wrapper.className = `msg-row ${role}`;

  const bubble = document.createElement("div");
  bubble.className = `msg ${role}`;

  if (isTyping) {
    bubble.classList.add("typing");
    bubble.innerHTML = `<span></span><span></span><span></span>`;
  } else {
    bubble.innerHTML = marked.parse(content); // renders **bold**, lists, etc. properly
    const time = document.createElement("div");
    time.className = "msg-time";
    time.textContent = timeNow();
    bubble.appendChild(time);
  }

  wrapper.appendChild(bubble);
  messagesEl.appendChild(wrapper);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return wrapper;
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = inputEl.value.trim();
  if (!message) return;

  addMessage("user", message);
  history.push({ role: "user", content: message });
  inputEl.value = "";

  const typingEl = addMessage("assistant", "", { isTyping: true });

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ message, history: history.slice(0, -1) }),
    });

    typingEl.remove();

    if (res.status === 401) {
      window.location.href = "/";
      return;
    }

    const data = await res.json();
    addMessage("assistant", data.reply);
    history.push({ role: "assistant", content: data.reply });
  } catch (err) {
    typingEl.remove();
    addMessage("assistant", "Error contacting the server.");
  }
});