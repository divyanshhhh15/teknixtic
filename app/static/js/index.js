// Teknixtic AI chat logic (moved from inline <script> in index.html)

const chatWindow = document.getElementById('chatWindow');
const sendBtn = document.getElementById('sendBtn');
const chatInput = document.getElementById('chatInput');
const chatBody = document.getElementById('chatBody');

if (chatWindow) {
  chatWindow.classList.add('show');
}

function formatBulletPoints(text) {
  const cleaned = String(text || '').trim();
  if (!cleaned) return '';

  if (/^\s*([-*•]|\d+\.)\s+/m.test(cleaned)) {
    return `<ul class="ai-bullet-list">${cleaned
      .split('\n')
      .filter(line => line.trim())
      .map(line => `<li>${line.replace(/^\s*[-*•]\s*/, '').trim()}</li>`)
      .join('')}</ul>`;
  }

  const parts = cleaned
    .split(/(?<=[.!?])\s+/)
    .map(part => part.trim())
    .filter(Boolean);

  if (parts.length > 1) {
    return `<ul class="ai-bullet-list">${parts
      .map(part => `<li>${part.replace(/^[-*•]\s*/, '')}</li>`)
      .join('')}</ul>`;
  }

  return `<ul class="ai-bullet-list"><li>${cleaned}</li></ul>`;
}

function addMessage(text, type) {
  if (!chatBody) return;

  const msg = document.createElement('div');
  msg.className = 'message ' + type;

  msg.innerHTML = `
    <div class="bubble">${text}</div>
  `;

  chatBody.appendChild(msg);
  chatBody.scrollTop = chatBody.scrollHeight;
}

async function sendMessage() {
  if (!chatInput) return;

  const text = chatInput.value.trim();
  if (!text) return;

  // Add user message
  addMessage(text, 'user');
  chatInput.value = '';

  // Typing animation
  const typingMessage = document.createElement('div');
  typingMessage.className = 'message ai';
  typingMessage.innerHTML = `
    <div class="bubble">
      <div class="typing">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  `;

  if (chatBody) {
    chatBody.appendChild(typingMessage);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  try {
    const response = await fetch('/chatbot/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: text
      })
    });

    const data = await response.json();

    typingMessage.remove();

    // Backend returns { response: '...' }
    addMessage(formatBulletPoints(data.response), 'ai');

    // Backend currently does NOT return videos.
    // Guard so UI won't break if videos is missing.
    if (data.videos && Array.isArray(data.videos) && data.videos.length > 0) {
      let videoHTML = '<div class="ai-videos">📺 Related Videos:<br>';

      data.videos.forEach(v => {
        videoHTML += `
      <a href="${v.url}" target="_blank" class="video-link">
        ▶ ${v.title}
      </a><br>
    `;
      });

      videoHTML += '</div>';
      addMessage(videoHTML, 'ai');
    }
  } catch (error) {
    typingMessage.remove();
    addMessage('⚠️ Teknixtic AI is unavailable right now. Please try again.', 'ai');
    console.error(error);
  }
}

if (sendBtn) {
  sendBtn.addEventListener('click', sendMessage);
}

if (chatInput) {
  chatInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
}

document.querySelectorAll('.quick-prompt').forEach(btn => {
  btn.addEventListener('click', () => {
    if (!chatInput) return;

    const preset = btn.getAttribute('data-preset');
    if (preset === 'generate-notes') {
      chatInput.value = 'Generate notes for the topic: ';
    } else {
      chatInput.value = btn.innerText;
    }

    sendMessage();
  });
});

function focusChatInput() {
  if (!chatInput) return;
  chatInput.focus();
}

function openBotAndFocus() {
  // The chat is already rendered on the home page; we just need to bring attention.
  // Ensure window scrolls to the chat area.
  const bot = document.getElementById('teknixtic-chatbot');
  if (bot) bot.scrollIntoView({ behavior: 'smooth', block: 'center' });
  focusChatInput();
}

const btnGenerateNotes = document.getElementById('btn-generate-notes');
const btnTryAIChat = document.getElementById('btn-try-ai-chat');

if (btnGenerateNotes) {
  btnGenerateNotes.addEventListener('click', () => {
    openBotAndFocus();
    if (chatInput) chatInput.value = 'Generate notes for the topic: ';
  });
}

if (btnTryAIChat) {
  btnTryAIChat.addEventListener('click', () => {
    openBotAndFocus();
  });
}

// Bot toggle + drag (bottom-right fixed to avoid fluctuation)
document.addEventListener("DOMContentLoaded", function () {
  const panel = document.getElementById("teknixtic-chat-panel");
  const fab = document.getElementById("teknixtic-fab");

  if (!panel || !fab) return;

  // Start hidden
  panel.classList.add('hidden');

  fab.addEventListener('click', () => {
    panel.classList.toggle('hidden');
  });

  let isDragging = false;
  let offsetX = 0;
  let offsetY = 0;

  panel.addEventListener('mousedown', (e) => {
    if (panel.classList.contains('hidden')) return;

    isDragging = true;
    const rect = panel.getBoundingClientRect();
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;

    panel.classList.add('dragging');
  });

  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    requestAnimationFrame(() => {
      // Keep fixed bottom-right: update only transform so layout doesn't fight
      const x = e.clientX - offsetX;
      const y = e.clientY - offsetY;

      const dx = x - (window.innerWidth - panel.offsetWidth - 20);
      const dy = y - (window.innerHeight - panel.offsetHeight - 20);

      panel.style.transform = `translate(${dx}px, ${dy}px)`;
    });
  });

  document.addEventListener('mouseup', () => {
    isDragging = false;
    panel.classList.remove('dragging');
  });
});

