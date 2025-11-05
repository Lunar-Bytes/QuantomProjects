const socket = io();
const username = "{{ username }}";
const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("send-btn");

sendBtn.onclick = () => {
  const message = messageInput.value.trim();
  if (!message) return;
  socket.send(`${username}: ${message}`);
  messageInput.value = "";
};

socket.on("message", msg => {
  const msgDiv = document.createElement("div");
  msgDiv.className = "msg";
  const [name, ...text] = msg.split(":");
  msgDiv.innerHTML = `<span class="username">${name}</span>: ${text.join(":")}`;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
});
