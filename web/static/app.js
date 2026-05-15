let activeChatId = null;

const chatList = document.getElementById("chat-list");
const messagesDiv = document.getElementById("messages");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const newChatBtn = document.getElementById("new-chat-btn");


// ─────────────────────────────
// Load chats
// ─────────────────────────────

async function loadChats() {

    const res = await fetch("/api/chats");
    const chats = await res.json();

    chatList.innerHTML = "";

    chats.forEach(chat => {

        const div = document.createElement("div");

        div.className = "chat-item";
        div.innerText = chat.name;

        if (chat.id === activeChatId) {
            div.classList.add("active");
        }

        div.onclick = () => loadChat(chat.id);

        chatList.appendChild(div);
    });
}


// ─────────────────────────────
// Create chat
// ─────────────────────────────

async function createChat() {

    const name = prompt("Chat name:") || "New Chat";

    const res = await fetch("/api/chats", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ name })
    });

    const data = await res.json();

    await loadChats();
    await loadChat(data.chat_id);
}


// ─────────────────────────────
// Load chat
// ─────────────────────────────

async function loadChat(chatId) {

    activeChatId = chatId;

    await fetch("/api/load_chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ chat_id: chatId })
    });

    const res = await fetch("/api/messages");
    const messages = await res.json();

    messagesDiv.innerHTML = "";

    messages.forEach(addMessageToUI);

    loadChats();
}


// ─────────────────────────────
// Send message
// ─────────────────────────────

async function sendMessage() {

    const text = input.value.trim();

    if (!text) return;

    if (!activeChatId) {
        alert("Create or load a chat first.");
        return;
    }

    addMessageToUI({
        role: "user",
        content: text
    });

    input.value = "";

    const thinking = document.createElement("div");
    thinking.className = "message assistant";
    thinking.id = "thinking";

    thinking.innerHTML = `
        <div class="bubble">Thinking...</div>
    `;

    messagesDiv.appendChild(thinking);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;


    const res = await fetch("/api/message", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: text
        })
    });

    const data = await res.json();

    document.getElementById("thinking")?.remove();

    addMessageToUI({
        role: "assistant",
        content: data.full
    });
}


// ─────────────────────────────
// Add message to UI
// ─────────────────────────────

function addMessageToUI(msg) {

    const div = document.createElement("div");

    div.className = `message ${msg.role}`;

    div.innerHTML = `
        <div class="bubble">${escapeHtml(msg.content)}</div>
    `;

    messagesDiv.appendChild(div);

    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}


// ─────────────────────────────
// Escape HTML
// ─────────────────────────────

function escapeHtml(text) {
    const div = document.createElement("div");
    div.innerText = text;
    return div.innerHTML;
}


// ─────────────────────────────
// Events
// ─────────────────────────────

sendBtn.onclick = sendMessage;
newChatBtn.onclick = createChat;

input.addEventListener("keydown", (e) => {

    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});


// ─────────────────────────────
// Init
// ─────────────────────────────

loadChats();

// ─────────────────────────────
// Voice recording
// ─────────────────────────────

let mediaRecorder = null;
let audioChunks   = [];
let isRecording   = false;

const micBtn   = document.getElementById("mic-btn");
const voiceBar = document.getElementById("voice-bar");

micBtn.onclick = async () => {
    if (!activeChatId) { alert("Create or load a chat first."); return; }
    if (!isRecording) { await startRecording(); } else { stopRecording(); }
};

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioChunks  = [];
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach(t => t.stop());
            await submitVoice();
        };
        mediaRecorder.start();
        isRecording = true;
        micBtn.textContent = "⏹";
        micBtn.style.color = "#f44336";
        voiceBar.style.display = "block";
    } catch (e) {
        alert("Microphone access denied.");
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        micBtn.textContent = "🎤";
        micBtn.style.color = "";
        voiceBar.style.display = "none";
    }
}

async function submitVoice() {
    const blob     = new Blob(audioChunks, { type: "audio/webm" });
    const formData = new FormData();
    formData.append("audio", blob, "voice_input.webm");

    const thinking = document.createElement("div");
    thinking.className = "message assistant";
    thinking.id = "thinking-voice";
    thinking.innerHTML = `<div class="bubble">Transcribing...</div>`;
    messagesDiv.appendChild(thinking);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    try {
        const res  = await fetch("/api/voice", { method: "POST", body: formData });
        const data = await res.json();
        document.getElementById("thinking-voice")?.remove();

        if (data.error) {
            addMessageToUI({ role: "assistant", content: "⚠ " + data.error });
        } else {
            addMessageToUI({ role: "user",      content: "🎤 " + (data.user_message || "") });
            addMessageToUI({ role: "assistant", content: data.full });
        }
    } catch (e) {
        document.getElementById("thinking-voice")?.remove();
        addMessageToUI({ role: "assistant", content: "⚠ Voice pipeline failed." });
    }
}