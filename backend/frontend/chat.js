const API_BASE = window.ECO_API_BASE || "http://localhost:8000";

let conversationId = null;

// Extract conversation_id from URL params (for Odoo webhook flow)
const urlParams = new URLSearchParams(window.location.search);
const urlConvId = urlParams.get("conversation_id");

async function initChat() {
  const messagesEl = document.getElementById("messages");

  if (urlConvId) {
    // Resume existing conversation (from Odoo webhook link)
    conversationId = urlConvId;
    try {
      const res = await fetch(`${API_BASE}/api/conversation/${conversationId}`);
      if (res.ok) {
        const data = await res.json();
        appendMessage("assistant", data.message);
        return;
      }
    } catch (_) {}
  }

  // Start fresh conversation
  try {
    const res = await fetch(`${API_BASE}/api/conversation/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const data = await res.json();
    conversationId = data.conversation_id;
    appendMessage("assistant", data.message);
  } catch (err) {
    appendMessage("assistant", "⚠️ Prepáčte, momentálne máme technické ťažkosti. Skúste neskôr alebo nás kontaktujte na info@ecoprodukt.sk");
  }
}

function appendMessage(role, text) {
  const messagesEl = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  // Render markdown-like formatting
  bubble.innerHTML = formatText(text);

  div.appendChild(bubble);
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function formatText(text) {
  // Detect proposal block (starts with ━━━)
  if (text.includes("━━━━━━")) {
    const parts = text.split(/(━━━━━━━━━━━━━━━━━━━━━━━━━[\s\S]*?━━━━━━━━━━━━━━━━━━━━━━━━━)/);
    return parts.map((part, i) => {
      if (part.startsWith("━━━")) {
        return `<div class="proposal">${escapeAndFormat(part)}</div>`;
      }
      return `<span>${escapeAndFormat(part)}</span>`;
    }).join("");
  }
  return escapeAndFormat(text);
}

function escapeAndFormat(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/_(.+?)_/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
}

function showTyping() {
  const messagesEl = document.getElementById("messages");
  const div = document.createElement("div");
  div.id = "typing-indicator";
  div.className = "typing";
  div.innerHTML = "<span></span><span></span><span></span>";
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTyping() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}

async function sendMessage() {
  const input = document.getElementById("message-input");
  const sendBtn = document.getElementById("send-btn");
  const text = input.value.trim();

  if (!text || !conversationId) return;

  input.value = "";
  input.style.height = "auto";
  sendBtn.disabled = true;

  appendMessage("user", text);
  showTyping();

  try {
    const res = await fetch(`${API_BASE}/api/conversation/${conversationId}/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: text }),
    });

    hideTyping();

    if (!res.ok) {
      appendMessage("assistant", "⚠️ Niečo sa pokazilo. Skúste znova.");
      return;
    }

    const data = await res.json();
    appendMessage("assistant", data.message);

    // Show CTA button if proposal was generated
    if (data.state === "proposal") {
      showProposalCTA();
    }
  } catch (err) {
    hideTyping();
    appendMessage("assistant", "⚠️ Problém s pripojením. Skontrolujte internet a skúste znova.");
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

function showProposalCTA() {
  const existing = document.getElementById("proposal-cta");
  if (existing) return;

  const messagesEl = document.getElementById("messages");
  const cta = document.createElement("div");
  cta.id = "proposal-cta";
  cta.style.cssText = "display:flex;gap:8px;flex-wrap:wrap;justify-content:center;padding:8px 0;";
  cta.innerHTML = `
    <button onclick="sendQuickReply('Chcem dohodnúť bezplatnú obhliadku')" style="background:#2e7d32;color:white;border:none;border-radius:20px;padding:10px 20px;font-size:13px;cursor:pointer;font-weight:600;">
      📅 Dohodniť obhliadku
    </button>
    <button onclick="sendQuickReply('Pošlite mi ponuku na email')" style="background:white;color:#2e7d32;border:2px solid #2e7d32;border-radius:20px;padding:10px 20px;font-size:13px;cursor:pointer;font-weight:600;">
      📧 Poslať ponuku emailom
    </button>
  `;
  messagesEl.appendChild(cta);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function sendQuickReply(text) {
  document.getElementById("message-input").value = text;
  sendMessage();
}

// Auto-resize textarea
document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("message-input");
  const sendBtn = document.getElementById("send-btn");

  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 100) + "px";
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  sendBtn.addEventListener("click", sendMessage);

  initChat();
});
