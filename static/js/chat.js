const socket = io();

const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("send");

// Ensure OLD_MESSAGES is an array
const msgs = Array.isArray(OLD_MESSAGES) ? OLD_MESSAGES : [];

// Load old messages
msgs.forEach(msg => {
    const div = document.createElement("div");
    div.textContent = `[${msg.time}] ${msg.user}: ${msg.text}`;
    chatBox.appendChild(div);
});
chatBox.scrollTop = chatBox.scrollHeight;

// Send message
sendBtn.addEventListener("click", () => {
    const text = messageInput.value.trim();
    if (text !== "") {
        socket.emit("send_message", { text: text });
        messageInput.value = "";
    }
});

// Receive live messages
socket.on("receive_message", (data) => {
    const newMsg = document.createElement("div");
    newMsg.textContent = `[${data.time}] ${data.user}: ${data.text}`;
    chatBox.appendChild(newMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
});

// Optional: Press Enter to send
messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendBtn.click();
});
