import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Zap,
  Wrench,
  Brain,
  LogOut,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  User,
} from "lucide-react";

const Sidebar = ({ user, logout, openAuthDialog }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  const menuItems = [
    { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
    { icon: Zap, label: "Agents", path: "/agents" },
    { icon: Wrench, label: "Tools", path: "/tools" },
    { icon: Brain, label: "Intelligence", path: "/intelligence" },
  ];

  return (
    <div
      className={`glass-heavy border-r border-white/10 transition-all duration-300 ${
        collapsed ? "w-20" : "w-64"
      } flex flex-col`}
    >
      <div className="p-6 border-b border-white/10 flex items-center justify-between">
        {!collapsed && (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-neon-purple to-neon-cyan rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="heading-font text-xl bg-gradient-to-r from-neon-purple to-neon-cyan bg-clip-text text-transparent">
              VAELIS
            </span>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          data-testid="sidebar-toggle"
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              data-testid={`sidebar-${item.label.toLowerCase()}`}
              className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${
                isActive
                  ? "bg-neon-purple text-white"
                  : "hover:bg-white/10 text-gray-400 hover:text-white"
              }`}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="body-font">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/10">
        {user ? (
          <>
            {!collapsed && (
              <div className="mb-3 p-3 glass-light rounded-xl">
                <div className="body-font text-sm text-gray-300">{user.name}</div>
                <div className="code-font text-xs text-gray-500">{user.email}</div>
              </div>
            )}
            <button
              onClick={logout}
              data-testid="sidebar-logout"
              className="w-full flex items-center gap-3 p-3 hover:bg-red-500/20 text-red-400 rounded-xl transition-colors"
            >
              <LogOut className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="body-font">Logout</span>}
            </button>
          </>
        ) : (
          <button
            onClick={openAuthDialog}
            data-testid="sidebar-login"
            className="w-full flex items-center gap-3 p-3 bg-neon-purple hover:bg-neon-cyan text-white rounded-xl transition-colors"
          >
            <User className="w-5 h-5 flex-shrink-0" />
            {!collapsed && <span className="body-font">Login</span>}
          </button>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
