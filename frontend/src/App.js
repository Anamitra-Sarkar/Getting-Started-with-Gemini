import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Landing from "./pages/Landing";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import Agents from "./pages/Agents";
import Tools from "./pages/Tools";
import Intelligence from "./pages/Intelligence";
import { Toaster } from "./components/ui/sonner";
import apiService from "./services/api";
import "./App.css";

function App() {
  const [token, setToken] = useState(localStorage.getItem("vaelis_token"));
  const [user, setUser] = useState(null);
  const [showAuthDialog, setShowAuthDialog] = useState(false);

  useEffect(() => {
    if (token) {
      localStorage.setItem("vaelis_token", token);
      apiService.setToken(token); // Set token in API service
      fetchUser();
    } else {
      localStorage.removeItem("vaelis_token");
      apiService.setToken(null);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const data = await apiService.getAccountInfo();
      setUser(data);
    } catch (error) {
      console.error("Failed to fetch user", error);
      // Don't clear token on fetch failure - backend might be down
      // setToken(null);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  const openAuthDialog = () => {
    setShowAuthDialog(true);
  };

  return (
    <div className="App min-h-screen">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route
            path="/auth"
            element={
              token ? <Navigate to="/dashboard" /> : <Auth setToken={setToken} />
            }
          />
          <Route
            path="/dashboard"
            element={
              <Dashboard user={user} logout={logout} token={token} openAuthDialog={openAuthDialog} />
            }
          />
          <Route
            path="/agents"
            element={
              <Agents user={user} logout={logout} token={token} openAuthDialog={openAuthDialog} />
            }
          />
          <Route
            path="/tools"
            element={
              <Tools user={user} logout={logout} token={token} openAuthDialog={openAuthDialog} />
            }
          />
          <Route
            path="/intelligence"
            element={
              <Intelligence user={user} logout={logout} token={token} openAuthDialog={openAuthDialog} />
            }
          />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
      {showAuthDialog && <Auth setToken={setToken} onClose={() => setShowAuthDialog(false)} isDialog={true} />}
    </div>
  );
}

export default App;