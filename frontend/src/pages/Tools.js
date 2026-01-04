import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Sidebar from "../components/Sidebar";
import apiService from "../services/api";
import * as Icons from "lucide-react";
import { toast } from "sonner";

const Tools = ({ user, logout, token, openAuthDialog }) => {
  const [tools, setTools] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedTool, setSelectedTool] = useState(null);
  const [toolInput, setToolInput] = useState("");
  const [toolResult, setToolResult] = useState(null);

  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    try {
      const data = await apiService.getTools();
      setTools(data.tools || data);
    } catch (error) {
      if (error.isServerDown) {
        toast.error("Server down");
      }
      console.error("Failed to fetch tools", error);
    }
  };

  const executeTool = async () => {
    if (!toolInput.trim()) {
      toast.error("Please provide input");
      return;
    }

    try {
      const data = await apiService.executeTool(selectedTool.id, { prompt: toolInput });
      setToolResult(data);
      toast.success("Tool executed successfully");
    } catch (error) {
      if (error.isServerDown) {
        toast.error("Server down");
      } else {
        toast.error(error.message || "Tool execution failed");
      }
    }
  };

  const categories = [...new Set(tools.map((t) => t.category))];
  const filteredTools =
    selectedCategory === "all"
      ? tools
      : tools.filter((t) => t.category === selectedCategory);

  return (
    <div className="flex min-h-screen bg-void text-white">
      <Sidebar user={user} logout={logout} openAuthDialog={openAuthDialog} />

      <div className="flex-1 p-8">
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
          <div className="mb-12">
            <h1 className="heading-font text-5xl mb-2">TOOLS HUB</h1>
            <p className="body-font text-gray-400">40+ pre-seeded tools for every domain</p>
          </div>

          <div className="flex gap-3 mb-8 overflow-x-auto pb-2">
            <button
              onClick={() => setSelectedCategory("all")}
              data-testid="category-all"
              className={`px-4 py-2 rounded-lg heading-font text-xs tracking-widest transition-colors ${
                selectedCategory === "all"
                  ? "bg-neon-purple text-white"
                  : "glass-light text-gray-400 hover:text-white"
              }`}
            >
              ALL
            </button>
            {categories.map((cat, idx) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                data-testid={`category-${cat}`}
                className={`px-4 py-2 rounded-lg heading-font text-xs tracking-widest transition-colors whitespace-nowrap ${
                  selectedCategory === cat
                    ? "bg-neon-purple text-white"
                    : "glass-light text-gray-400 hover:text-white"
                }`}
              >
                {cat.toUpperCase()}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {filteredTools.map((tool, idx) => {
              const Icon = Icons[tool.icon] || Icons.Sparkles;
              return (
                <motion.button
                  key={tool.id}
                  initial={{ y: 50, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: idx * 0.05 }}
                  onClick={() => setSelectedTool(tool)}
                  data-testid={`tool-card-${idx}`}
                  className="glass-heavy rounded-2xl p-6 hover:border-neon-cyan/50 transition-all text-left"
                >
                  <Icon className="w-10 h-10 text-neon-purple mb-4" />
                  <h3 className="heading-font text-lg mb-2">{tool.name}</h3>
                  <p className="body-font text-sm text-gray-400">{tool.description}</p>
                  <div className="mt-4 inline-block px-3 py-1 glass-light rounded-full">
                    <span className="label-font text-neon-cyan">{tool.category}</span>
                  </div>
                </motion.button>
              );
            })}
          </div>
        </motion.div>
      </div>

      {selectedTool && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedTool(null)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={(e) => e.stopPropagation()}
            className="glass-heavy rounded-3xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            data-testid="tool-modal"
          >
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center gap-4">
                {(() => {
                  const Icon = Icons[selectedTool.icon] || Icons.Sparkles;
                  return <Icon className="w-12 h-12 text-neon-purple" />;
                })()}
                <div>
                  <h2 className="heading-font text-2xl">{selectedTool.name}</h2>
                  <p className="body-font text-sm text-gray-400">
                    {selectedTool.description}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedTool(null)}
                data-testid="close-tool-modal"
                className="text-gray-400 hover:text-white"
              >
                <Icons.X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="label-font block mb-2">INPUT</label>
                <textarea
                  value={toolInput}
                  onChange={(e) => setToolInput(e.target.value)}
                  data-testid="tool-input"
                  className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:border-neon-cyan focus:outline-none h-32 resize-none"
                  placeholder="Enter your input..."
                />
              </div>

              <button
                onClick={executeTool}
                data-testid="execute-tool-button"
                className="w-full py-4 bg-neon-purple hover:bg-neon-cyan text-white heading-font text-sm tracking-widest rounded-xl transition-colors neon-glow"
              >
                EXECUTE TOOL
              </button>

              {toolResult && (
                <div className="glass-light rounded-xl p-6" data-testid="tool-result">
                  <h3 className="label-font mb-4">RESULT</h3>
                  {toolResult.images && toolResult.images.length > 0 ? (
                    <div className="space-y-4">
                      {toolResult.images.map((img, idx) => (
                        <img
                          key={idx}
                          src={`data:${img.mime_type};base64,${img.data}`}
                          alt="Generated"
                          className="w-full rounded-lg"
                        />
                      ))}
                      {toolResult.text && (
                        <p className="body-font text-sm text-gray-300">{toolResult.text}</p>
                      )}
                    </div>
                  ) : (
                    <p className="body-font text-gray-300">
                      {JSON.stringify(toolResult, null, 2)}
                    </p>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Tools;