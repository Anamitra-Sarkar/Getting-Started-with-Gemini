import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import Sidebar from "../components/Sidebar";
import apiService from "../services/api";
import { Brain, Send, Sparkles, User, Paperclip, Image, FileText, Music, Video, X } from "lucide-react";
import { toast } from "sonner";

const Intelligence = ({ user, logout, token, openAuthDialog }) => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [attachments, setAttachments] = useState([]);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [input]);

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files || []);
    const newAttachments = files.map(file => ({
      file,
      name: file.name,
      type: file.type,
      size: file.size,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null
    }));
    setAttachments(prev => [...prev, ...newAttachments]);
  };

  const removeAttachment = (index) => {
    setAttachments(prev => {
      const newAttachments = [...prev];
      // Revoke object URL if it's an image
      if (newAttachments[index].preview) {
        URL.revokeObjectURL(newAttachments[index].preview);
      }
      newAttachments.splice(index, 1);
      return newAttachments;
    });
  };

  const triggerFileInput = (accept = "*") => {
    if (fileInputRef.current) {
      fileInputRef.current.accept = accept;
      fileInputRef.current.click();
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if ((!input.trim() && attachments.length === 0) || loading) return;

    const userMessage = {
      role: "user",
      content: input,
      attachments: attachments.map(att => ({
        name: att.name,
        type: att.type,
        preview: att.preview
      }))
    };
    
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    const currentAttachments = attachments;
    setInput("");
    setAttachments([]);
    setLoading(true);

    try {
      // NOTE: File upload to backend is not yet implemented
      // Currently attachments are only displayed in the UI
      // Backend integration requires:
      // 1. GridFS file storage setup
      // 2. Multipart form-data handling in /ai/generate
      // 3. File metadata storage in MongoDB
      // For now, we only send the text prompt
      const data = await apiService.chatWithAI(currentInput, "think", false);
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

  const handleKeyDown = (e) => {
    // Enter to send, Shift+Enter for newline
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e);
    }
  };

  return (
    <div className="flex min-h-screen bg-void text-white">
      <Sidebar user={user} logout={logout} openAuthDialog={openAuthDialog} />

      <div className="flex-1 flex flex-col w-full md:w-auto">
        <div className="p-4 md:p-8 border-b border-white/10">
          <h1 className="heading-font text-2xl md:text-4xl mb-2 ml-12 md:ml-0">INTELLIGENCE ANALYSIS</h1>
          <p className="body-font text-sm md:text-base text-gray-400 ml-12 md:ml-0">
            AI-powered reasoning and cognitive analysis with file support
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-4 md:space-y-6" data-testid="chat-messages">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <div className="w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-neon-purple to-neon-cyan rounded-2xl flex items-center justify-center mb-4 md:mb-6">
                <Sparkles className="w-8 h-8 md:w-12 md:h-12 text-white" />
              </div>
              <h2 className="heading-font text-2xl md:text-3xl mb-4">VAELIS INTELLIGENCE</h2>
              <p className="body-font text-sm md:text-base text-gray-400 max-w-md">
                Ask me to analyze text, detect biases, assess reasoning, or identify intent.
                You can also attach images, documents, audio, and video files.
              </p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-2 md:gap-4 ${msg.role === "user" ? "justify-end" : ""}`}
              data-testid={`message-${idx}`}
            >
              {msg.role === "assistant" && (
                <div className="w-8 h-8 md:w-10 md:h-10 bg-gradient-to-br from-neon-purple to-neon-cyan rounded-xl flex items-center justify-center flex-shrink-0">
                  <Brain className="w-4 h-4 md:w-6 md:h-6 text-white" />
                </div>
              )}
              <div
                className={`max-w-full md:max-w-3xl ${
                  msg.role === "user"
                    ? "bg-neon-purple rounded-2xl p-3 md:p-4"
                    : "glass-heavy rounded-2xl p-4 md:p-6"
                }`}
                style={{
                  wordWrap: 'break-word',
                  overflowWrap: 'break-word',
                  whiteSpace: 'pre-wrap',
                  maxWidth: msg.role === "user" ? '85%' : '100%'
                }}
              >
                <p className="body-font text-sm md:text-base leading-relaxed">
                  {msg.content}
                </p>
                {msg.attachments && msg.attachments.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {msg.attachments.map((att, attIdx) => (
                      <div key={attIdx} className="relative">
                        {att.preview ? (
                          <img
                            src={att.preview}
                            alt={att.name}
                            className="w-24 h-24 md:w-32 md:h-32 object-cover rounded-lg"
                          />
                        ) : (
                          <div className="w-24 h-24 md:w-32 md:h-32 bg-white/10 rounded-lg flex flex-col items-center justify-center p-2">
                            <FileText className="w-6 h-6 md:w-8 md:h-8 text-gray-400 mb-1" />
                            <span className="text-xs text-gray-400 text-center truncate w-full px-1">
                              {att.name}
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {msg.role === "user" && (
                <div className="w-8 h-8 md:w-10 md:h-10 bg-white/10 rounded-xl flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 md:w-6 md:h-6 text-gray-400" />
                </div>
              )}
            </motion.div>
          ))}

          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-2 md:gap-4"
            >
              <div className="w-8 h-8 md:w-10 md:h-10 bg-gradient-to-br from-neon-purple to-neon-cyan rounded-xl flex items-center justify-center">
                <Brain className="w-4 h-4 md:w-6 md:h-6 text-white animate-pulse" />
              </div>
              <div className="glass-heavy rounded-2xl p-4 md:p-6">
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

        <div className="p-4 md:p-8 border-t border-white/10">
          <form onSubmit={sendMessage} className="max-w-4xl mx-auto">
            {/* Attachment previews */}
            {attachments.length > 0 && (
              <div className="mb-4 flex flex-wrap gap-2">
                {attachments.map((att, idx) => (
                  <div key={idx} className="relative group">
                    {att.preview ? (
                      <div className="relative">
                        <img
                          src={att.preview}
                          alt={att.name}
                          className="w-16 h-16 md:w-20 md:h-20 object-cover rounded-lg"
                        />
                        <button
                          type="button"
                          onClick={() => removeAttachment(idx)}
                          className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity"
                          aria-label={`Remove ${att.name}`}
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ) : (
                      <div className="relative w-16 h-16 md:w-20 md:h-20 bg-white/10 rounded-lg flex flex-col items-center justify-center p-1">
                        <FileText className="w-4 h-4 md:w-6 md:h-6 text-gray-400 mb-1" />
                        <span className="text-xs text-gray-400 text-center truncate w-full px-1">
                          {att.name.substring(0, 6)}...
                        </span>
                        <button
                          type="button"
                          onClick={() => removeAttachment(idx)}
                          className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity"
                          aria-label={`Remove ${att.name}`}
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            <div className="glass-heavy rounded-2xl p-2 flex flex-col gap-2">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                data-testid="chat-input"
                placeholder="Ask me to analyze... (Shift+Enter for new line)"
                aria-label="Chat message input"
                className="flex-1 px-3 py-2 md:px-4 md:py-3 bg-transparent text-white placeholder:text-gray-600 focus:outline-none body-font resize-none overflow-y-auto text-sm md:text-base"
                style={{ 
                  minHeight: '48px',
                  maxHeight: '200px'
                }}
                disabled={loading}
                rows={1}
              />
              
              <div className="flex gap-1 md:gap-2 items-center px-2">
                {/* Attachment buttons */}
                <button
                  type="button"
                  onClick={() => triggerFileInput('image/*')}
                  disabled={loading}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50"
                  aria-label="Attach image"
                  title="Attach image"
                >
                  <Image className="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
                </button>
                <button
                  type="button"
                  onClick={() => triggerFileInput('audio/*')}
                  disabled={loading}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50 hidden sm:block"
                  aria-label="Attach audio"
                  title="Attach audio"
                >
                  <Music className="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
                </button>
                <button
                  type="button"
                  onClick={() => triggerFileInput('video/*')}
                  disabled={loading}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50 hidden sm:block"
                  aria-label="Attach video"
                  title="Attach video"
                >
                  <Video className="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
                </button>
                <button
                  type="button"
                  onClick={() => triggerFileInput('.pdf,.doc,.docx,.txt')}
                  disabled={loading}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50"
                  aria-label="Attach document"
                  title="Attach document"
                >
                  <Paperclip className="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
                </button>
                
                <div className="flex-1" />
                
                <button
                  type="submit"
                  data-testid="send-message-button"
                  disabled={loading || (!input.trim() && attachments.length === 0)}
                  className="px-4 py-2 md:px-6 md:py-3 bg-neon-purple hover:bg-neon-cyan text-white rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  aria-label="Send message"
                >
                  <Send className="w-4 h-4 md:w-5 md:h-5" />
                </button>
              </div>
            </div>
            
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileSelect}
              className="hidden"
            />
          </form>
        </div>
      </div>
    </div>
  );
};

export default Intelligence;