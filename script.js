document
  .getElementById("chat-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const message = document.getElementById("message").value.trim();

    if (username === "" || message === "") {
      alert("Both fields are required.");
      return;
    }

    try {
      const response = await fetch("/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, message }),
      });

      if (!response.ok) {
        throw new Error("Server error");
      }

      document.getElementById("message").value = "";
    } catch (error) {
      console.error("Error sending message:", error);
    }
  });

async function fetchMessages() {
  try {
    const response = await fetch("/messages");
    if (!response.ok) throw new Error("Failed to fetch messages");

    const messages = await response.json();
    const list = document.getElementById("messages-list");
    list.innerHTML = "";

    messages.forEach((msg) => {
      const li = document.createElement("li");
      li.classList.add("list-group-item");
      li.textContent = `[${msg.date}] ${msg.username}: ${msg.message}`;
      list.appendChild(li);
    });
  } catch (error) {
    console.error("Error fetching messages:", error);
  }
}

setInterval(fetchMessages, 2000);
