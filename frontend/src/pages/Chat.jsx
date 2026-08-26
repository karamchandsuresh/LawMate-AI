import "./Chat.css";

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import ReactMarkdown from "react-markdown";

import remarkGfm from "remark-gfm";
import { useLanguage } from "../context/LanguageContext";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";


function Chat() {

  const navigate = useNavigate();
  const { t } = useLanguage();

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


    // Add user's message immediately

    setMessages((prev) => [

      ...prev,

      {
        sender: "user",

        text: userMessage,
      },

    ]);


    // Clear input

    setMessage("");


    // Show thinking bubble

    setIsLoading(true);


    try {

      const response = await fetch(

        `${API_BASE_URL}/chat`,

        {

          method: "POST",

          headers: {

            "Content-Type": "application/json",

          },

          body: JSON.stringify({

            message: userMessage,

          }),

        }

      );


      if (!response.ok) {

        throw new Error(

          `Backend error: ${response.status}`

        );

      }


      const data = await response.json();


      setMessages((prev) => [

        ...prev,

        {

          sender: "ai",

          text: data.reply,

          route: data.route || null,

          actionLabel: data.action_label || null,

        },

      ]);

    }


    catch (error) {

      console.error("Chat error:", error);


      setMessages((prev) => [

        ...prev,

        {

          sender: "ai",

          text:

            "❌ Sorry, something went wrong. Please try again.",

        },

      ]);

    }


    finally {

      setIsLoading(false);

    }

  };


  const handleKeyDown = (event) => {

    // Enter → Send

    if (

      event.key === "Enter" &&

      !event.shiftKey

    ) {

      event.preventDefault();

      sendMessage();

    }

    // Shift + Enter → New line

    // Default browser behavior is preserved

  };


  return (

    <div className="chat-page">


      <h1>{t.chat.title}</h1>


      <p>

        {t.chat.intro}

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

                  <ReactMarkdown

                    remarkPlugins={[remarkGfm]}

                  >

                    {msg.text}

                  </ReactMarkdown>

                ) : (

                  <div className="user-message-text">

                    {msg.text}

                  </div>

                )}


              {msg.sender === "ai" &&
                  msg.route &&
                  msg.actionLabel && (

                    <button
                      className="chat-route-button"
                      onClick={() =>
                        navigate(msg.route)
                      }
                    >
                      {msg.actionLabel}
                    </button>

                  )}

              </div>

            </div>

          ))}


          {/* THINKING BUBBLE */}

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

            placeholder={t.chat.placeholder}

            value={message}

            onChange={(event) =>

              setMessage(event.target.value)

            }

            onKeyDown={handleKeyDown}

            rows="1"

          />


          <button

            onClick={sendMessage}

            disabled={isLoading}

          >

            {isLoading

              ? t.chat.thinking

              : t.chat.send}

          </button>


        </div>


      </div>


    </div>

  );

}


export default Chat;