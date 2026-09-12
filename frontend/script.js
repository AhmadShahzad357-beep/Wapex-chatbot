const chat = document.getElementById("chat");
const form = document.getElementById("composer");
const input = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const resetBtn = document.getElementById("resetBtn");

const SESSION_KEY = "wapexp_session_id";

function getSessionId() {
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

function addMessage(text, role) {
  const msg = document.createElement("div");
  msg.className = `msg ${role}`;

  if (role === "bot" || role === "error") {
    const tag = document.createElement("span");
    tag.className = "msg-tag";
    tag.textContent = role === "error" ? "error" : "wapexp";
    msg.appendChild(tag);
  }

  const body = document.createElement("div");
  body.className = "msg-body";
  body.textContent = text;
  msg.appendChild(body);

  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
  return msg;
}

function addTyping() {
  const msg = document.createElement("div");
  msg.className = "msg bot";
  msg.id = "typingIndicator";
  const tag = document.createElement("span");
  tag.className = "msg-tag";
  tag.textContent = "wapexp";
  msg.appendChild(tag);
  const body = document.createElement("div");
  body.className = "msg-body typing";
  body.innerHTML = "<span></span><span></span><span></span>";
  msg.appendChild(body);
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById("typingIndicator");
  if (el) el.remove();
}

async function sendMessage(message) {
  addMessage(message, "user");
  input.value = "";
  sendBtn.disabled = true;
  addTyping();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: getSessionId() }),
    });

    if (!res.ok) throw new Error(`Server returned ${res.status}`);

    const data = await res.json();
    removeTyping();
    addMessage(data.reply, "bot");
  } catch (err) {
    removeTyping();
    addMessage("Connection failed. Please check the server and try again.", "error");
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const value = input.value.trim();
  if (!value) return;
  sendMessage(value);
});

resetBtn.addEventListener("click", () => {
  localStorage.removeItem(SESSION_KEY);
  chat.innerHTML = "";
  addMessage(
    "Naya conversation shuru ho gaya hai. Courses, fees, timings ya location ke baare mein poochiye.",
    "bot"
  );
});
