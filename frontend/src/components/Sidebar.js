import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Zap,
  Brain,
  LogOut,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  User,
  Menu,
  X as CloseIcon,
} from "lucide-react";

const Sidebar = ({ user, logout, openAuthDialog }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) {
        setMobileOpen(false);
      }
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const menuItems = [
    { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
    { icon: Zap, label: "Agents", path: "/agents" },
    { icon: Brain, label: "Intelligence", path: "/intelligence" },
  ];

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  return (
    <>
      {/* Mobile hamburger button */}
      {isMobile && (
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="fixed top-4 left-4 z-50 p-3 glass-heavy rounded-xl md:hidden"
          aria-label="Toggle menu"
        >
          {mobileOpen ? (
            <CloseIcon className="w-6 h-6" />
          ) : (
            <Menu className="w-6 h-6" />
          )}
        </button>
      )}

      {/* Overlay for mobile */}
      {isMobile && mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`glass-heavy border-r border-white/10 transition-all duration-300 flex flex-col z-40
          ${isMobile ? 'fixed top-0 left-0 h-full' : 'relative'}
          ${isMobile && !mobileOpen ? '-translate-x-full' : 'translate-x-0'}
          ${!isMobile && collapsed ? "w-20" : "w-64"}`}
      >
        <div className="p-6 border-b border-white/10 flex items-center justify-between">
          {(!collapsed || isMobile) && (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-neon-purple to-neon-cyan rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <span className="heading-font text-xl bg-gradient-to-r from-neon-purple to-neon-cyan bg-clip-text text-transparent">
                VAELIS
              </span>
            </div>
          )}
          {!isMobile && (
            <button
              onClick={() => setCollapsed(!collapsed)}
              data-testid="sidebar-toggle"
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {collapsed ? (
                <ChevronRight className="w-5 h-5" />
              ) : (
                <ChevronLeft className="w-5 h-5" />
              )}
            </button>
          )}
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.path}
                onClick={() => handleNavigation(item.path)}
                data-testid={`sidebar-${item.label.toLowerCase()}`}
                className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${
                  isActive
                    ? "bg-neon-purple text-white"
                    : "hover:bg-white/10 text-gray-400 hover:text-white"
                }`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {(!collapsed || isMobile) && <span className="body-font">{item.label}</span>}
              </button>
            );
          })}
        </nav>

        <div className="p-4 border-t border-white/10">
          {user ? (
            <>
              {(!collapsed || isMobile) && (
                <div className="mb-3 p-3 glass-light rounded-xl">
                  <div className="body-font text-sm text-gray-300 truncate">{user.name || user.email}</div>
                  <div className="code-font text-xs text-gray-500 truncate">{user.email}</div>
                </div>
              )}
              <button
                onClick={() => {
                  logout();
                  if (isMobile) setMobileOpen(false);
                }}
                data-testid="sidebar-logout"
                className="w-full flex items-center gap-3 p-3 hover:bg-red-500/20 text-red-400 rounded-xl transition-colors"
              >
                <LogOut className="w-5 h-5 flex-shrink-0" />
                {(!collapsed || isMobile) && <span className="body-font">Logout</span>}
              </button>
            </>
          ) : (
            <button
              onClick={() => {
                openAuthDialog();
                if (isMobile) setMobileOpen(false);
              }}
              data-testid="sidebar-login"
              className="w-full flex items-center gap-3 p-3 bg-neon-purple hover:bg-neon-cyan text-white rounded-xl transition-colors"
            >
              <User className="w-5 h-5 flex-shrink-0" />
              {(!collapsed || isMobile) && <span className="body-font">Login</span>}
            </button>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;
