import React, { createContext, useContext, useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  LuLayoutDashboard, LuUsers, LuTrendingUp, LuGift, 
  LuHistory, LuUser, LuLogOut, LuMenu, LuX, LuLock, LuUserPlus 
} from 'react-icons/lu';

// Set up Axios Base URL
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Global Authentication Context
interface AuthContextType {
  token: string | null;
  user: any | null;
  loading: boolean;
  login: (token: string) => void;
  logout: () => void;
  fetchProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};

// Axios Request Interceptor to auto-attach Bearer JWT Token
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth Provider Component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [user, setUser] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const response = await axios.get('/api/profile');
      setUser(response.data);
    } catch (error) {
      logout();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, loading, login, logout, fetchProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected Layout with Sidebar and Top Navbar
const DashboardLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LuLayoutDashboard },
    { name: 'Supplier Management', href: '/suppliers', icon: LuUsers },
    { name: 'Freight Predictor', href: '/predict', icon: LuTrendingUp },
    { name: 'Recommendation Engine', href: '/recommend', icon: LuGift },
    { name: 'History Logs', href: '/history', icon: LuHistory },
    { name: 'User Profile', href: '/profile', icon: LuUser },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row">
      {/* Sidebar for desktop */}
      <aside className={`fixed inset-y-0 z-50 flex flex-col w-64 bg-slate-900 text-slate-300 transform transition-transform duration-200 ease-in-out md:translate-x-0 md:static ${sidebarOpen ? 'translate-x-0' : '-translate-x-0 -left-64'}`}>
        <div className="flex items-center justify-between h-16 px-6 bg-slate-950 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <div className="h-9 w-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg">FS</div>
            <span className="font-outfit font-bold text-xl text-white tracking-wide">FlowSense AI</span>
          </div>
          <button className="md:hidden text-slate-400 hover:text-white" onClick={() => setSidebarOpen(false)}>
            <LuX className="h-6 w-6" />
          </button>
        </div>
        
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const isActive = location.pathname === item.icon ? false : location.pathname.startsWith(item.href);
            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg font-medium text-sm transition-colors ${isActive ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'hover:bg-slate-800 hover:text-white'}`}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800 bg-slate-950/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="h-9 w-9 rounded-full bg-slate-700 flex items-center justify-center text-white font-semibold">
                {user?.username?.substring(0, 2).toUpperCase()}
              </div>
              <div className="truncate w-28">
                <p className="text-sm font-semibold text-white truncate">{user?.username}</p>
                <p className="text-xs text-slate-400 truncate">Administrator</p>
              </div>
            </div>
            <button onClick={handleLogout} className="p-2 text-slate-400 hover:text-red-400 rounded-lg hover:bg-slate-800 transition-colors" title="Logout">
              <LuLogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 sticky top-0 z-30">
          <div className="flex items-center">
            <button className="md:hidden text-slate-500 hover:text-slate-900 mr-4" onClick={() => setSidebarOpen(true)}>
              <LuMenu className="h-6 w-6" />
            </button>
            <h1 className="font-outfit font-bold text-lg text-slate-800 hidden sm:block">Smart Procurement & Freight Cost Prediction</h1>
            <span className="sm:hidden font-outfit font-bold text-lg text-slate-800">FlowSense AI</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              Academic Project (AI & DS)
            </span>
            <div className="h-8 w-px bg-slate-200"></div>
            <div className="text-sm text-slate-500">
              User: <span className="font-semibold text-slate-700">{user?.username}</span>
            </div>
          </div>
        </header>

        {/* Dynamic Route Content */}
        <main className="flex-1 p-6 overflow-y-auto max-w-7xl w-full mx-auto">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/suppliers" element={<Suppliers />} />
            <Route path="/predict" element={<Predictor />} />
            <Route path="/recommend" element={<Recommendations />} />
            <Route path="/history" element={<History />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

// Route wrapper for authenticated users
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center">
        <div className="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="mt-4 text-slate-600 font-medium animate-pulse">Loading FlowSense AI...</p>
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/splash" replace />;
  }

  return <>{children}</>;
};

// Placeholder imports for pages. We will write these files separately!
import Splash from './pages/Splash';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Suppliers from './pages/Suppliers';
import Predictor from './pages/Predictor';
import Recommendations from './pages/Recommendations';
import History from './pages/History';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/splash" element={<Splash />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/404" element={<NotFound />} />
          
          <Route path="/*" element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
