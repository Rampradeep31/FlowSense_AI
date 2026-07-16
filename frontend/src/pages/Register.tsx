import React, { useState } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../App';
import { LuLock, LuUser, LuShieldAlert, LuCheck } from 'react-icons/lu';

const Register: React.FC = () => {
  const { token } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // If already logged in, redirect to dashboard
  if (token) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      await axios.post('/api/register', { username, password });
      setSuccess("Account registered successfully! Redirecting to login...");
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Registration failed. Please make sure the FastAPI server is running.");
      }
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center py-12 px-6">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl shadow-xl">
        {/* Title */}
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 rounded-xl bg-blue-100 text-blue-600 items-center justify-center font-bold text-2xl mx-auto">FS</div>
          <h2 className="font-outfit font-bold text-2xl text-slate-900">Create FlowSense AI Account</h2>
          <p className="text-sm text-slate-500">Sign up to register as an administrator/procurement coordinator</p>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg flex items-start space-x-2 text-sm">
            <LuShieldAlert className="h-5 w-5 flex-shrink-0 mt-0.5 text-red-500" />
            <span>{error}</span>
          </div>
        )}

        {/* Success Banner */}
        {success && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 p-3 rounded-lg flex items-start space-x-2 text-sm">
            <LuCheck className="h-5 w-5 flex-shrink-0 mt-0.5 text-emerald-500" />
            <span>{success}</span>
          </div>
        )}

        {/* Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <LuUser className="h-5 w-5" />
                </div>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="pl-10 block w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
                  placeholder="Create username (min 3 chars)"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <LuLock className="h-5 w-5" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 block w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
                  placeholder="Create password (min 6 chars)"
                />
              </div>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                Confirm Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <LuLock className="h-5 w-5" />
                </div>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="pl-10 block w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
                  placeholder="Re-enter password"
                />
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors disabled:opacity-50"
            >
              {submitting ? "Registering account..." : "Register Account"}
            </button>
          </div>
        </form>

        {/* Login link */}
        <div className="text-center text-sm text-slate-500 mt-4">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-500 transition-colors">
            Login here
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
