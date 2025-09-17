import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Lock, Server } from 'lucide-react';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const LoginPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm({
    defaultValues: {
      vastHost: '10.143.11.204',
      vastPort: '443',
      username: '',
      password: '',
      tenant: 'default'
    }
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    
    try {
      const result = await login({
        vastHost: data.vastHost,
        vastPort: parseInt(data.vastPort),
        username: data.username,
        password: data.password,
        tenant: data.tenant
      });

      if (result.success) {
        toast.success('Login successful!');
        navigate('/', { replace: true });
      } else {
        toast.error(result.message || 'Login failed');
      }
    } catch (error) {
      toast.error('An unexpected error occurred');
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Connecting to VAST..." />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Server className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">VAST Services</h1>
          <p className="text-gray-600 mt-2">Connect to your VAST cluster</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* VAST Host */}
          <div>
            <label htmlFor="vastHost" className="block text-sm font-medium text-gray-700 mb-1">
              VAST Host
            </label>
            <input
              id="vastHost"
              type="text"
              {...register('vastHost', {
                required: 'VAST host is required',
                pattern: {
                  value: /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/,
                  message: 'Please enter a valid IP address'
                }
              })}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.vastHost ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="10.143.11.204"
            />
            {errors.vastHost && (
              <p className="mt-1 text-sm text-red-600">{errors.vastHost.message}</p>
            )}
          </div>

          {/* VAST Port */}
          <div>
            <label htmlFor="vastPort" className="block text-sm font-medium text-gray-700 mb-1">
              Port
            </label>
            <input
              id="vastPort"
              type="number"
              {...register('vastPort', {
                required: 'Port is required',
                min: { value: 1, message: 'Port must be greater than 0' },
                max: { value: 65535, message: 'Port must be less than 65536' }
              })}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.vastPort ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="443"
            />
            {errors.vastPort && (
              <p className="mt-1 text-sm text-red-600">{errors.vastPort.message}</p>
            )}
          </div>

          {/* Username */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              id="username"
              type="text"
              {...register('username', { required: 'Username is required' })}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.username ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="admin"
            />
            {errors.username && (
              <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
            )}
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              {...register('password', { required: 'Password is required' })}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.password ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="••••••••"
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
            )}
          </div>

          {/* Tenant */}
          <div>
            <label htmlFor="tenant" className="block text-sm font-medium text-gray-700 mb-1">
              Tenant
            </label>
            <input
              id="tenant"
              type="text"
              {...register('tenant')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="default"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Connecting...
              </>
            ) : (
              <>
                <Lock className="w-4 h-4 mr-2" />
                Connect to VAST
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;