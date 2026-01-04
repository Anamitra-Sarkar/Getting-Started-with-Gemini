import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import apiService from "../services/api";
import { toast } from "sonner";
import {
  Activity,
  Zap,
  Target,
  TrendingUp,
  Brain,
  Sparkles,
} from "lucide-react";

const Dashboard = ({ user, logout, token, openAuthDialog }) => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    agents: 0,
    runs: 0,
    tools: 20,
    intelligence_score: 87,
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await apiService.getDashboardStats();
      setStats(data);
    } catch (error) {
      if (error.isServerDown) {
        toast.error("Server down");
      }
      console.error("Failed to fetch stats", error);
    }
  };

  const statCards = [
    {
      icon: Zap,
      label: "Active Agents",
      value: stats.agents,
      color: "neon-purple",
    },
    {
      icon: Activity,
      label: "Total Runs",
      value: stats.runs,
      color: "neon-cyan",
    },
    {
      icon: Target,
      label: "Available Tools",
      value: stats.tools,
      color: "neon-pink",
    },
    {
      icon: Brain,
      label: "Intelligence Score",
      value: `${stats.intelligence_score}%`,
      color: "neon-purple",
    },
  ];

  return (
    <div className="flex min-h-screen bg-void text-white">
      <Sidebar user={user} logout={logout} openAuthDialog={openAuthDialog} />

      <div className="flex-1 p-8">
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
        >
          <div className="flex justify-between items-start mb-12">
            <div>
              <h1 className="heading-font text-5xl mb-2">COMMAND CENTER</h1>
              <p className="body-font text-gray-400">
                Welcome back, {user?.name || "Intelligence Officer"}
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => navigate("/agents")}
                data-testid="new-agent-button"
                className="px-6 py-3 bg-neon-purple hover:bg-neon-cyan text-white heading-font text-xs tracking-widest rounded-lg transition-colors neon-glow"
              >
                NEW AGENT
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {statCards.map((stat, idx) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={idx}
                  initial={{ y: 50, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: idx * 0.1 }}
                  className="glass-heavy rounded-2xl p-6 border-l-4"
                  style={{ borderColor: `var(--${stat.color})` }}
                  data-testid={`stat-card-${idx}`}
                >
                  <Icon className="w-10 h-10 mb-4 text-neon-cyan" />
                  <div className="heading-font text-3xl mb-1">{stat.value}</div>
                  <div className="body-font text-sm text-gray-400">{stat.label}</div>
                </motion.div>
              );
            })}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
            <motion.div
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="glass-heavy rounded-2xl p-8"
            >
              <h2 className="heading-font text-2xl mb-6">QUICK ACTIONS</h2>
              <div className="space-y-3">
                <button
                  onClick={() => navigate("/agents")}
                  data-testid="quick-action-agents"
                  className="w-full p-4 glass-light rounded-xl hover:bg-white/10 transition-colors text-left flex items-center gap-3"
                >
                  <Zap className="w-5 h-5 text-neon-purple" />
                  <span className="body-font">Create New Agent</span>
                </button>
                <button
                  onClick={() => navigate("/tools")}
                  data-testid="quick-action-tools"
                  className="w-full p-4 glass-light rounded-xl hover:bg-white/10 transition-colors text-left flex items-center gap-3"
                >
                  <Target className="w-5 h-5 text-neon-cyan" />
                  <span className="body-font">Explore Tools Hub</span>
                </button>
                <button
                  onClick={() => navigate("/intelligence")}
                  data-testid="quick-action-intelligence"
                  className="w-full p-4 glass-light rounded-xl hover:bg-white/10 transition-colors text-left flex items-center gap-3"
                >
                  <Brain className="w-5 h-5 text-neon-pink" />
                  <span className="body-font">Run Intelligence Analysis</span>
                </button>
              </div>
            </motion.div>

            <motion.div
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="glass-heavy rounded-2xl p-8"
            >
              <h2 className="heading-font text-2xl mb-6">SYSTEM STATUS</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="body-font text-gray-400">AI Engine</span>
                  <span className="label-font text-green-400">OPERATIONAL</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="body-font text-gray-400">Agent Network</span>
                  <span className="label-font text-green-400">ACTIVE</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="body-font text-gray-400">Tools System</span>
                  <span className="label-font text-green-400">READY</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="body-font text-gray-400">Security</span>
                  <span className="label-font text-green-400">PROTECTED</span>
                </div>
              </div>
            </motion.div>
          </div>

          <motion.div
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="glass-heavy rounded-2xl p-8"
          >
            <h2 className="heading-font text-2xl mb-6">INTELLIGENCE CATEGORIES</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {[
                "Core Intelligence",
                "Agent System",
                "Tools Hub",
                "Web Intelligence",
                "Markets & Finance",
                "Health & Science",
                "Education",
                "Business Strategy",
                "Meta-Cognition",
                "Security",
                "Personal OS",
              ].map((cat, idx) => (
                <button
                  key={idx}
                  data-testid={`category-button-${idx}`}
                  className="p-4 glass-light rounded-xl hover:border-neon-cyan border border-white/5 transition-colors text-center"
                >
                  <Sparkles className="w-6 h-6 mx-auto mb-2 text-neon-purple" />
                  <span className="body-font text-xs">{cat}</span>
                </button>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;