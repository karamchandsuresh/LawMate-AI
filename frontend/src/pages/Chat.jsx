import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function Chat() {
  const [message, setMessage] = useState("");

  const [isLoading, setIsLoading] = useState(false);

  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hello! 👋\n\nHow can I assist you with your legal question today?",
    },
  ]);

  const sendMessage = async () => {
    if (!message.trim() || isLoading) return;

    const userMessage = message;

    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text: userMessage,
      },
    ]);

    setMessage("");

    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          message: userMessage,
        }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: data.reply,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: "❌ Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      sendMessage();
    }
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

          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.sender}`}
            >
              <div className="ai-response">

                {msg.sender === "ai" ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.text}
                  </ReactMarkdown>
                ) : (
                  msg.text
                )}

              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message ai thinking">

              <span>
                LawMate AI is thinking
              </span>

              <span className="dots">

                <span>.</span>
                <span>.</span>
                <span>.</span>

              </span>

            </div>
          )}

        </div>

        <div className="chat-input">

          <input
            type="text"
            placeholder="Ask your legal question..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
          />

          <button
            onClick={sendMessage}
            disabled={isLoading}
          >
            {isLoading ? "Thinking..." : "Send"}
          </button>

        </div>

      </div>

    </div>
  );
}

export default Chat;