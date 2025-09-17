import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { 
  Home, 
  Database, 
  Server, 
  MessageSquare, 
  BarChart3, 
  Settings, 
  LogOut,
  User
} from 'lucide-react';

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Database Schemas', href: '/schemas', icon: Database },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (href) => {
    if (href === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">VAST Services</h1>
          <p className="text-sm text-gray-600 mt-1">
            {user?.vastHost}
          </p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Main
          </div>
          {navigation.map((item) => (
            <button
              key={item.name}
              onClick={() => navigate(item.href)}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                isActive(item.href)
                  ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <item.icon className={`w-5 h-5 ${
                isActive(item.href) ? 'text-blue-700' : 'text-gray-400'
              }`} />
              <span className="font-medium">{item.name}</span>
            </button>
          ))}

          <div className="pt-6">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Services
            </div>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="px-3 py-2">Virtual Servers</div>
              <div className="px-3 py-2">Container Services</div>
              <div className="px-3 py-2">GPU Computing</div>
              <div className="px-3 py-2">Vector DB</div>
              <div className="px-3 py-2">Functions</div>
              <div className="px-3 py-2">Kafka</div>
            </div>
          </div>
        </nav>

        {/* User Section */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">{user?.username}</p>
              <p className="text-xs text-gray-500">{user?.tenant}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-2 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span className="text-sm">Logout</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                {location.pathname === '/' ? 'Dashboard' : 
                 location.pathname === '/schemas' ? 'Database Schemas' : 
                 'VAST Services'}
              </h2>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Region: africa-east-1
              </span>
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;