import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import Sidebar from "../components/Sidebar";
import apiService from "../services/api";
import { Brain, Send, Sparkles, User } from "lucide-react";
import { toast } from "sonner";

const Intelligence = ({ user, logout, token, openAuthDialog }) => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const data = await apiService.chatWithAI(input, "think", false);
      const aiMessage = { role: "assistant", content: data.output || data.analysis || "Analysis complete." };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      if (error.isServerDown) {
        toast.error("Server down");
      } else {
        toast.error("Analysis failed");
      }
      const errorMessage = {
        role: "assistant",
        content: "I apologize, but I encountered an error processing your request.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-void text-white">
      <Sidebar user={user} logout={logout} openAuthDialog={openAuthDialog} />

      <div className="flex-1 flex flex-col">
        <div className="p-8 border-b border-white/10">
          <h1 className="heading-font text-4xl mb-2">INTELLIGENCE ANALYSIS</h1>
          <p className="body-font text-gray-400">
            AI-powered reasoning and cognitive analysis - Chat interface
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-8 space-y-6" data-testid="chat-messages">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-neon-purple to-neon-cyan rounded-2xl flex items-center justify-center mb-6">
                <Sparkles className="w-12 h-12 text-white" />
              </div>
              <h2 className="heading-font text-3xl mb-4">VAELIS INTELLIGENCE</h2>
              <p className="body-font text-gray-400 max-w-md">
                Ask me to analyze text, detect biases, assess reasoning, or identify intent.
                I'm powered by advanced AI models.
              </p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-4 ${msg.role === "user" ? "justify-end" : ""}`}
              data-testid={`message-${idx}`}
            >
              {msg.role === "assistant" && (
                <div className="w-10 h-10 bg-gradient-to-br from-neon-purple to-neon-cyan rounded-xl flex items-center justify-center flex-shrink-0">
                  <Brain className="w-6 h-6 text-white" />
                </div>
              )}
              <div
                className={`max-w-3xl ${
                  msg.role === "user"
                    ? "bg-neon-purple rounded-2xl p-4"
                    : "glass-heavy rounded-2xl p-6"
                }`}
              >
                <p className="body-font text-base leading-relaxed whitespace-pre-wrap">
                  {msg.content}
                </p>
              </div>
              {msg.role === "user" && (
                <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center flex-shrink-0">
                  <User className="w-6 h-6 text-gray-400" />
                </div>
              )}
            </motion.div>
          ))}

          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-4"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-neon-purple to-neon-cyan rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6 text-white animate-pulse" />
              </div>
              <div className="glass-heavy rounded-2xl p-6">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" />
                  <div
                    className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  />
                  <div
                    className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce"
                    style={{ animationDelay: "0.4s" }}
                  />
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="p-8 border-t border-white/10">
          <form onSubmit={sendMessage} className="max-w-4xl mx-auto">
            <div className="glass-heavy rounded-2xl p-2 flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                data-testid="chat-input"
                placeholder="Ask me to analyze text, detect bias, assess reasoning..."
                className="flex-1 px-4 py-3 bg-transparent text-white placeholder:text-gray-600 focus:outline-none body-font"
                disabled={loading}
              />
              <button
                type="submit"
                data-testid="send-message-button"
                disabled={loading || !input.trim()}
                className="px-6 py-3 bg-neon-purple hover:bg-neon-cyan text-white rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Intelligence;