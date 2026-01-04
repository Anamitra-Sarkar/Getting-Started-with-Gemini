import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Sidebar from "../components/Sidebar";
import apiService from "../services/api";
import { Plus, Play, Pause, Trash2, Clock, Brain } from "lucide-react";
import { toast } from "sonner";

const Agents = ({ user, logout, token, openAuthDialog }) => {
  const [agents, setAgents] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    category: "general",
    prompt: "",
    memory_scope: "conversation",
  });

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const data = await apiService.getAgents();
      setAgents(data.agents || data);
    } catch (error) {
      if (error.isServerDown) {
        toast.error("Server down");
      }
      console.error("Failed to fetch agents", error);
    }
  };

  const createAgent = async (e) => {
    e.preventDefault();
    try {
      await apiService.createAgent(formData);
      toast.success("Agent created successfully");
      setShowCreate(false);
      fetchAgents();
      setFormData({
        name: "",
        description: "",
        category: "general",
        prompt: "",
        memory_scope: "conversation",
      });
    } catch (error) {
      if (error.isServerDown) {
        toast.error("Server down");
      } else {
        toast.error(error.message || "Failed to create agent");
      }
    }
  };

  const deleteAgent = async (id) => {
    try {
      await apiService.deleteAgent(id);
      toast.success("Agent deleted");
      fetchAgents();
    } catch (error) {
      toast.error(error.message || "Failed to delete agent");
    }
  };

  return (
    <div className="flex min-h-screen bg-void text-white">
      <Sidebar user={user} logout={logout} openAuthDialog={openAuthDialog} />

      <div className="flex-1 p-8">
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
          <div className="flex justify-between items-start mb-12">
            <div>
              <h1 className="heading-font text-5xl mb-2">AGENT SYSTEM</h1>
              <p className="body-font text-gray-400">
                Create and manage autonomous AI agents
              </p>
            </div>
            <button
              onClick={() => setShowCreate(!showCreate)}
              data-testid="create-agent-button"
              className="px-6 py-3 bg-neon-purple hover:bg-neon-cyan text-white heading-font text-xs tracking-widest rounded-lg transition-colors neon-glow flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              NEW AGENT
            </button>
          </div>

          {showCreate && (
            <motion.div
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              className="glass-heavy rounded-2xl p-8 mb-8"
            >
              <h2 className="heading-font text-2xl mb-6">CREATE AGENT</h2>
              <form onSubmit={createAgent} className="space-y-4" data-testid="create-agent-form">
                <div>
                  <label className="label-font block mb-2">AGENT NAME</label>
                  <input
                    type="text"
                    data-testid="agent-name-input"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:border-neon-cyan focus:outline-none"
                    placeholder="e.g., Market Analyzer"
                    required
                  />
                </div>
                <div>
                  <label className="label-font block mb-2">DESCRIPTION</label>
                  <input
                    type="text"
                    data-testid="agent-description-input"
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                    className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:border-neon-cyan focus:outline-none"
                    placeholder="What does this agent do?"
                    required
                  />
                </div>
                <div>
                  <label className="label-font block mb-2">SYSTEM PROMPT</label>
                  <textarea
                    data-testid="agent-prompt-input"
                    value={formData.prompt}
                    onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
                    className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:border-neon-cyan focus:outline-none h-32 resize-none"
                    placeholder="You are an AI agent that..."
                    required
                  />
                </div>
                <div className="flex gap-4">
                  <button
                    type="submit"
                    data-testid="submit-agent-button"
                    className="px-8 py-3 bg-neon-purple hover:bg-neon-cyan text-white heading-font text-xs tracking-widest rounded-lg transition-colors"
                  >
                    CREATE
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreate(false)}
                    data-testid="cancel-agent-button"
                    className="px-8 py-3 glass-light hover:bg-white/10 text-white heading-font text-xs tracking-widest rounded-lg transition-colors"
                  >
                    CANCEL
                  </button>
                </div>
              </form>
            </motion.div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent, idx) => (
              <motion.div
                key={agent.id}
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: idx * 0.1 }}
                className="glass-heavy rounded-2xl p-6 hover:border-neon-cyan/50 transition-all"
                data-testid={`agent-card-${idx}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <Brain className="w-10 h-10 text-neon-purple" />
                  <div className="flex gap-2">
                    <button
                      data-testid={`delete-agent-${idx}`}
                      onClick={() => deleteAgent(agent.id)}
                      className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </button>
                  </div>
                </div>
                <h3 className="heading-font text-xl mb-2">{agent.name}</h3>
                <p className="body-font text-sm text-gray-400 mb-4">{agent.description}</p>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Clock className="w-3 h-3" />
                  <span>
                    {new Date(agent.created_at).toLocaleDateString()}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>

          {agents.length === 0 && !showCreate && (
            <div className="glass-heavy rounded-2xl p-16 text-center">
              <Brain className="w-20 h-20 mx-auto mb-4 text-gray-600" />
              <h3 className="heading-font text-2xl mb-2">NO AGENTS YET</h3>
              <p className="body-font text-gray-400 mb-6">
                Create your first autonomous AI agent
              </p>
              <button
                onClick={() => setShowCreate(true)}
                data-testid="empty-state-create-button"
                className="px-8 py-3 bg-neon-purple hover:bg-neon-cyan text-white heading-font text-xs tracking-widest rounded-lg transition-colors neon-glow"
              >
                CREATE AGENT
              </button>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Agents;