import React from 'react';
import { Link } from 'react-router-dom';
import { LuShieldAlert, LuArrowLeft } from 'react-icons/lu';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center justify-center p-6 text-center">
      <div className="max-w-md w-full space-y-6">
        <div className="inline-flex h-20 w-20 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-500 items-center justify-center animate-bounce">
          <LuShieldAlert className="h-10 w-10" />
        </div>
        <div className="space-y-2">
          <h1 className="text-5xl font-extrabold font-outfit text-white">404</h1>
          <h2 className="text-xl font-bold font-outfit text-slate-350">Route Not Found</h2>
          <p className="text-slate-400 text-sm max-w-sm mx-auto leading-relaxed">
            The endpoint or UI path you are looking for has either been moved or does not exist. Check route parameters.
          </p>
        </div>
        <div className="pt-4">
          <Link
            to="/dashboard"
            className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2.5 rounded-lg shadow-lg shadow-blue-500/20 transition-all text-sm"
          >
            <LuArrowLeft className="h-4 w-4" />
            <span>Return to Dashboard</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
