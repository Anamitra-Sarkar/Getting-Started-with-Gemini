import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Mail, Lock, User, X } from "lucide-react";
import { toast } from "sonner";
import { auth, isFirebaseConfigured } from "../config/firebase";
import { 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword,
  updateProfile
} from "firebase/auth";

// Use environment variable if defined, otherwise fallback to production backend
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://getting-started-with-gemini.onrender.com';

const Auth = ({ setToken, onClose, isDialog }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Use Firebase Auth if configured, otherwise fallback to simple JWT auth
      if (isFirebaseConfigured && auth) {
        await handleFirebaseAuth();
      } else {
        await handleSimpleAuth();
      }
    } catch (error) {
      // Error handling is done in the individual auth methods
      console.error("Auth error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFirebaseAuth = async () => {
    try {
      let userCredential;
      
      if (isLogin) {
        // Firebase sign in
        userCredential = await signInWithEmailAndPassword(auth, formData.email, formData.password);
      } else {
        // Firebase sign up
        userCredential = await createUserWithEmailAndPassword(auth, formData.email, formData.password);
        
        // Update user profile with name
        if (formData.name) {
          await updateProfile(userCredential.user, {
            displayName: formData.name
          });
        }
      }

      // Get Firebase ID token
      const idToken = await userCredential.user.getIdToken();
      
      // Set the Firebase token (backend will verify it)
      setToken(idToken);
      toast.success(`Welcome ${isLogin ? 'back' : 'to Vaelis'}!`);
      if (isDialog && onClose) onClose();
      
    } catch (error) {
      console.error("Firebase auth error:", error);
      
      // User-friendly error messages
      let errorMessage = "Authentication failed";
      if (error.code === 'auth/email-already-in-use') {
        errorMessage = "Email already in use";
      } else if (error.code === 'auth/invalid-email') {
        errorMessage = "Invalid email address";
      } else if (error.code === 'auth/user-not-found' || error.code === 'auth/wrong-password') {
        errorMessage = "Invalid email or password";
      } else if (error.code === 'auth/weak-password') {
        errorMessage = "Password should be at least 6 characters";
      } else if (error.code === 'auth/network-request-failed') {
        errorMessage = "Network error. Please check your connection";
      }
      
      toast.error(errorMessage);
      throw error;
    }
  };

  const handleSimpleAuth = async () => {
    try {
      const endpoint = isLogin ? "/api/auth/login" : "/api/auth/register";
      const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        setToken(data.token);
        toast.success(`Welcome ${isLogin ? 'back' : 'to Vaelis'}!`);
        if (isDialog && onClose) onClose();
      } else {
        toast.error(data.detail || "Authentication failed");
        throw new Error(data.detail || "Authentication failed");
      }
    } catch (error) {
      if (error.message !== "Authentication failed") {
        toast.error("Server down");
      }
      throw error;
    }
  };

  const content = (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="relative z-10 w-full max-w-md mx-auto"
      style={{ marginTop: isDialog ? "5rem" : "0" }}
    >
      <div className="glass-heavy rounded-3xl p-10">
        {isDialog && (
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 hover:bg-white/10 rounded-lg transition-colors"
            data-testid="auth-close-button"
          >
            <X className="w-5 h-5" />
          </button>
        )}
          
          <div className="flex items-center justify-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-neon-purple to-neon-cyan rounded-2xl flex items-center justify-center">
              <Sparkles className="w-10 h-10 text-white" />
            </div>
          </div>

          <h1 className="heading-font text-3xl text-center mb-2">
            {isLogin ? "WELCOME BACK" : "JOIN VAELIS"}
          </h1>
          <p className="body-font text-center text-gray-400 mb-8">
            {isLogin ? "Access your intelligence hub" : "Create your account"}
          </p>

          <form onSubmit={handleSubmit} className="space-y-5" data-testid="auth-form">
            {!isLogin && (
              <div>
                <label className="label-font block mb-2">NAME</label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="text"
                    data-testid="auth-name-input"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full pl-12 pr-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:border-neon-cyan focus:outline-none transition-colors"
                    placeholder="Your name"
                    required={!isLogin}
                  />
                </div>
              </div>
            )}

            <div>
              <label className="label-font block mb-2">EMAIL</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="email"
                  data-testid="auth-email-input"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full pl-12 pr-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:border-neon-cyan focus:outline-none transition-colors"
                  placeholder="your@email.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="label-font block mb-2">PASSWORD</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="password"
                  data-testid="auth-password-input"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-12 pr-4 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:border-neon-cyan focus:outline-none transition-colors"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              data-testid="auth-submit-button"
              disabled={loading}
              className="w-full py-4 bg-neon-purple hover:bg-neon-cyan text-white heading-font text-sm tracking-widest rounded-xl transition-all duration-300 neon-glow disabled:opacity-50"
            >
              {loading ? "PROCESSING..." : isLogin ? "ENTER SYSTEM" : "CREATE ACCOUNT"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => setIsLogin(!isLogin)}
              data-testid="auth-toggle-button"
              className="body-font text-sm text-gray-400 hover:text-neon-cyan transition-colors"
            >
              {isLogin ? "Need an account? Sign up" : "Already have an account? Log in"}
            </button>
          </div>
        </div>
      </motion.div>
  );

  if (isDialog) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4">
        {content}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-void text-white flex items-center justify-center p-4">
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage:
            "url(https://images.unsplash.com/photo-1595409300508-fa0e6fa98692?crop=entropy&cs=srgb&fm=jpg&q=85)",
          backgroundSize: "cover",
          backgroundPosition: "center",
          opacity: 0.1,
        }}
      />
      {content}
    </div>
  );
};

export default Auth;