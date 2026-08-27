import "./Chat.css";

import {
  useEffect,
  useMemo,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { useLanguage } from "../context/LanguageContext";
import { useAIModel } from "../context/AIModelContext";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

const CHAT_STORAGE_KEY =
  "lawmate-current-chat";

const INITIAL_MESSAGES = [
  {
    sender: "ai",
    text:
      "Hello! 👋\n\nHow can I assist you with your legal question today?",
  },
];

function loadStoredMessages() {
  try {
    const saved = localStorage.getItem(
      CHAT_STORAGE_KEY
    );

    if (!saved) {
      return INITIAL_MESSAGES;
    }

    const parsed = JSON.parse(saved);

    if (
      !Array.isArray(parsed)
      || parsed.length === 0
    ) {
      return INITIAL_MESSAGES;
    }

    return parsed;
  } catch (error) {
    console.error(
      "Unable to restore LawMate chat:",
      error
    );

    return INITIAL_MESSAGES;
  }
}

function Chat() {
  const navigate = useNavigate();

  const {
    t,
    language,
  } = useLanguage();

  const {
    aiMode,
  } = useAIModel();

  const [message, setMessage] =
    useState("");

  const [isLoading, setIsLoading] =
    useState(false);

  const [messages, setMessages] =
    useState(loadStoredMessages);

  useEffect(() => {
    try {
      localStorage.setItem(
        CHAT_STORAGE_KEY,
        JSON.stringify(messages)
      );
    } catch (error) {
      console.error(
        "Unable to save LawMate chat:",
        error
      );
    }
  }, [messages]);

  const conversationHistory = useMemo(
    () =>
      messages
        .filter(
          (item) =>
            item.sender === "user"
            || item.sender === "ai"
        )
        .slice(-8)
        .map((item) => ({
          sender: item.sender,
          text: item.text,
        })),
    [messages]
  );

  const startNewChat = () => {
    if (isLoading) {
      return;
    }

    setMessage("");
    setMessages(INITIAL_MESSAGES);

    try {
      localStorage.removeItem(
        CHAT_STORAGE_KEY
      );
    } catch (error) {
      console.error(
        "Unable to clear LawMate chat:",
        error
      );
    }
  };

  const sendMessage = async () => {
    if (
      !message.trim()
      || isLoading
    ) {
      return;
    }

    const userMessage =
      message.trim();

    const requestHistory =
      conversationHistory;

    setMessages((previous) => [
      ...previous,
      {
        sender: "user",
        text: userMessage,
      },
    ]);

    setMessage("");
    setIsLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            message: userMessage,
            ai_mode: aiMode,
            language,
            history: requestHistory,
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
          || `Backend error: ${response.status}`
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          sender: "ai",
          text:
            data.reply
            || "LawMate did not return a response.",
          route:
            data.route || null,
          actionLabel:
            data.action_label || null,
          provider:
            data.provider || null,
        },
      ]);
    } catch (error) {
      console.error(
        "Chat error:",
        error
      );

      setMessages((previous) => [
        ...previous,
        {
          sender: "ai",
          text:
            "❌ Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter"
      && !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-page">
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: "16px",
          flexWrap: "wrap",
          marginBottom: "8px",
        }}
      >
        <div>
          <h1>{t.chat.title}</h1>
          <p>{t.chat.intro}</p>
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-end",
            gap: "6px",
          }}
        >
          <button
            type="button"
            className="chat-route-button"
            onClick={startNewChat}
            disabled={isLoading}
          >
            ＋ New Chat
          </button>
        </div>
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map(
            (item, index) => (
              <div
                key={`${item.sender}-${index}`}
                className={
                  `message ${item.sender}`
                }
              >
                <div className="ai-response">
                  {item.sender === "ai" ? (
                    <ReactMarkdown
                      remarkPlugins={[
                        remarkGfm,
                      ]}
                    >
                      {item.text}
                    </ReactMarkdown>
                  ) : (
                    <div className="user-message-text">
                      {item.text}
                    </div>
                  )}

                  {
                    item.sender === "ai"
                    && item.route
                    && item.actionLabel
                    && (
                      <button
                        className="chat-route-button"
                        onClick={() =>
                          navigate(
                            item.route
                          )
                        }
                      >
                        {item.actionLabel}
                      </button>
                    )
                  }
                </div>
              </div>
            )
          )}

          {isLoading && (
            <div className="message ai thinking">
              <span>
                {t.chat.thinkingBubble}
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
          <textarea
            placeholder={
              t.chat.placeholder
            }
            value={message}
            onChange={(event) =>
              setMessage(
                event.target.value
              )
            }
            onKeyDown={
              handleKeyDown
            }
            rows="1"
          />

          <button
            onClick={sendMessage}
            disabled={isLoading}
          >
            {
              isLoading
                ? t.chat.thinking
                : t.chat.send
            }
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chat;
