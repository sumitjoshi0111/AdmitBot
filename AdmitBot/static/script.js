// script.js
// Handles the chat UI: sending messages to Flask, displaying
// responses, Enter key support, suggested questions, and Clear Chat.

const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-btn");
const suggestionButtons = document.querySelectorAll(".suggestion-btn");

function addMessage(text, sender) {
    const div = document.createElement("div");
    div.className = "message " + sender;
    div.textContent = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
}

function addLoadingIndicator() {
    const div = document.createElement("div");
    div.className = "message loading";
    div.textContent = "AdmitBot is typing...";
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
}

async function sendMessage(message) {
    if (!message || !message.trim()) {
        return;
    }

    addMessage(message, "user");
    userInput.value = "";

    const loadingEl = addLoadingIndicator();

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message }),
        });

        if (!res.ok) {
            throw new Error("Server error: " + res.status);
        }

        const data = await res.json();
        loadingEl.remove();
        addMessage(data.response, "bot");
    } catch (err) {
        loadingEl.remove();
        addMessage(
            "Sorry, something went wrong while contacting AdmitBot. Please try again.",
            "bot"
        );
        console.error(err);
    }
}

sendBtn.addEventListener("click", () => {
    sendMessage(userInput.value);
});

userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        sendMessage(userInput.value);
    }
});

suggestionButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
        sendMessage(btn.textContent);
    });
});

clearBtn.addEventListener("click", async () => {
    try {
        await fetch("/clear", { method: "POST" });
    } catch (err) {
        console.error(err);
    }
    chatBox.innerHTML = "";
    addMessage(
        "Hello! I am AdmitBot, your engineering admission assistant. Ask me about CAP, CET, cutoffs, or say 'my rank is 2500' to try a sample prediction.",
        "bot"
    );
});

// Initial greeting when the page loads.
window.addEventListener("DOMContentLoaded", () => {
    addMessage(
        "Hello! I am AdmitBot, your engineering admission assistant. Ask me about CAP, CET, cutoffs, or say 'my rank is 2500' to try a sample prediction.",
        "bot"
    );
});
