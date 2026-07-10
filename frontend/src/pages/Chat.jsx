function Chat() {
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

        </div>

        <div className="chat-input">

          <input
            type="text"
            placeholder="Ask your legal question..."
          />

          <button>Send</button>

        </div>

      </div>

    </div>
  );
}

export default Chat;