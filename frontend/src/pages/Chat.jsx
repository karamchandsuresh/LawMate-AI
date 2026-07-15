import { useState } from "react";

function Chat() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");

  const sendMessage = async () => {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
      }),
    });

    const data = await response.json();
    setReply(data.reply);
  };

  return (
    <div className="chat-page">
      <h1>⚖️ LawMate AI Assistant</h1>

      <p>
        Ask any legal question and receive AI-powered answers
        grounded in trusted Indian legal sources.
      </p>

      <div className="chat-container">
        <div className="chat-messages">
          <div className="message ai">
            <p>Hello! 👋</p>
            <p>How can I assist you with your legal question today?</p>
          </div>

          {reply && (
            <div className="message ai">
              <p>{reply}</p>
            </div>
          )}
        </div>

        <div className="chat-input">
          <input
            type="text"
            placeholder="Ask your legal question..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />

          <button onClick={sendMessage}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chat;