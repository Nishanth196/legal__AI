/**
 * LexReg AI – Chatbot JavaScript
 */
document.addEventListener('DOMContentLoaded', function () {
  loadChatHistory();
});

async function sendMessage() {
  const input   = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;

  input.value = '';
  appendMessage('user', message);
  showTyping();

  try {
    const r = await fetch('/api/chat', {
      method:  'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken':  getCSRF(),
      },
      body: JSON.stringify({ message }),
    });
    const data = await r.json();
    hideTyping();
    appendMessage('bot', data.response || 'Sorry, I could not process your request.');
    loadChatHistory();
  } catch (e) {
    hideTyping();
    appendMessage('bot', '⚠️ Connection error. Please try again.');
  }
}

function sendQuick(text) {
  document.getElementById('chatInput').value = text;
  sendMessage();
  // Hide quick prompts after first use
  const qp = document.getElementById('quickPrompts');
  if (qp) qp.style.display = 'none';
}

function appendMessage(role, text) {
  const container = document.getElementById('chatMessages');
  const time       = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

  const wrapper = document.createElement('div');
  wrapper.className = 'd-flex gap-3 ' + (role === 'user' ? 'flex-row-reverse' : '');

  const avatar = document.createElement('div');
  if (role === 'bot') {
    avatar.style.cssText = 'width:36px;height:36px;background:linear-gradient(135deg,#1e90ff,#0d1b4b);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;flex-shrink:0;';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
  } else {
    avatar.style.cssText = 'width:36px;height:36px;background:linear-gradient(135deg,#00c896,#00b894);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;flex-shrink:0;';
    avatar.innerHTML = '<i class="fas fa-user"></i>';
  }

  const bubble = document.createElement('div');
  const inner  = document.createElement('div');
  inner.className = 'chat-bubble ' + role;

  // Convert markdown-like formatting
  inner.innerHTML = formatMessage(text);

  const timeEl = document.createElement('div');
  timeEl.className = 'text-muted mt-1';
  timeEl.style.fontSize = '11px';
  timeEl.textContent    = time;
  timeEl.style.textAlign = role === 'user' ? 'right' : 'left';

  bubble.appendChild(inner);
  bubble.appendChild(timeEl);
  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  container.appendChild(wrapper);

  // Scroll to bottom
  container.scrollTop = container.scrollHeight;
}

function formatMessage(text) {
  // Convert **bold**, *italic*, bullet lists
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^• (.*)/gm, '<li>$1</li>')
    .replace(/^- (.*)/gm, '<li>$1</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>');
}

let typingEl = null;
function showTyping() {
  typingEl = document.createElement('div');
  typingEl.className = 'd-flex gap-3';
  typingEl.innerHTML = `
    <div style="width:36px;height:36px;background:linear-gradient(135deg,#1e90ff,#0d1b4b);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;flex-shrink:0;">
      <i class="fas fa-robot"></i>
    </div>
    <div class="chat-bubble bot" style="padding:12px 16px;">
      <div class="d-flex gap-1 align-items-center" style="height:20px;">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    </div>
  `;
  document.getElementById('chatMessages').appendChild(typingEl);
  document.getElementById('chatMessages').scrollTop = 99999;
}

function hideTyping() {
  if (typingEl) { typingEl.remove(); typingEl = null; }
}

async function loadChatHistory() {
  try {
    const r    = await fetch('/api/chat/history');
    const data = await r.json();
    const el   = document.getElementById('recentQueries');
    if (!el) return;
    if (!data.length) {
      el.innerHTML = '<div class="text-muted small text-center py-2">No history yet</div>';
      return;
    }
    el.innerHTML = data.slice(0, 5).map(h => `
      <div class="border-bottom py-2 px-1" style="cursor:pointer;"
           onclick="document.getElementById('chatInput').value='${h.message.replace(/'/g,"\\'")}'"
           title="${h.message}">
        <div class="small fw-600 text-truncate">${h.message.substring(0,50)}</div>
        <div style="font-size:11px;color:var(--text-muted);">${h.time}</div>
      </div>
    `).join('');
  } catch(e) {}
}

function clearChat() {
  const container = document.getElementById('chatMessages');
  container.innerHTML = '';
}

function getCSRF() {
  const el = document.querySelector('[name=csrf_token]');
  if (el) return el.value;
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

// Add typing dot CSS
const style = document.createElement('style');
style.textContent = `
.typing-dot {
  width: 8px; height: 8px;
  background: var(--accent);
  border-radius: 50%;
  animation: typingBounce 1.2s infinite ease-in-out;
}
.typing-dot:nth-child(2) { animation-delay: .2s; }
.typing-dot:nth-child(3) { animation-delay: .4s; }
@keyframes typingBounce {
  0%, 80%, 100% { transform: translateY(0); }
  40%           { transform: translateY(-8px); }
}
`;
document.head.appendChild(style);
