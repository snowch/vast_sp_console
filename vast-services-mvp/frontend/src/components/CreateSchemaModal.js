import React from 'react';
import { useForm } from 'react-hook-form';
import { X, Database, Info } from 'lucide-react';

const CreateSchemaModal = ({ onClose, onCreate, isLoading, connectionInfo }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch
  } = useForm({
    defaultValues: {
      name: '',
      description: ''
    }
  });

  const onSubmit = (data) => {
    onCreate(data);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Database className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Create Database Schema</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={isLoading}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Connection Info */}
        {connectionInfo && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Info className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">VAST Connection</span>
            </div>
            <div className="text-xs text-blue-700 space-y-1">
              <div><strong>Endpoint:</strong> {connectionInfo.endpoint}</div>
              <div><strong>Bucket:</strong> {connectionInfo.bucket}</div>
              <div className="flex items-center space-x-2">
                <strong>Status:</strong> 
                <span className="flex items-center space-x-1">
                  <div className={`w-2 h-2 rounded-full ${
                    connectionInfo.status === 'connected' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <span>{connectionInfo.status || 'connected'}</span>
                </span>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Schema Name *
            </label>
            <input
              id="name"
              {...register('name', {
                required: 'Schema name is required',
                pattern: {
                  value: /^[a-zA-Z][a-zA-Z0-9_]*$/,
                  message: 'Name must start with letter, contain only letters, numbers, underscore'
                },
                maxLength: {
                  value: 64,
                  message: 'Name must be 64 characters or less'
                }
              })}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="analytics_db"
              disabled={isLoading}
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              Schema will be created in bucket: <strong>{connectionInfo?.bucket || 'default'}</strong>
            </p>
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description <span className="text-gray-400">(optional)</span>
            </label>
            <textarea
              id="description"
              {...register('description', {
                maxLength: {
                  value: 255,
                  message: 'Description must be 255 characters or less'
                }
              })}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
                errors.description ? 'border-red-500' : 'border-gray-300'
              }`}
              rows="3"
              placeholder="Description of this database schema..."
              disabled={isLoading}
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
            )}
          </div>

          {/* Schema Info */}
          <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Schema Configuration</h4>
            <div className="text-xs text-gray-600 space-y-1">
              <div><strong>Protocols:</strong> DATABASE, S3</div>
              <div><strong>Path:</strong> /{connectionInfo?.bucket || 'bucket'}/[schema-name]</div>
              <div><strong>Features:</strong> Tables, Queries, Indexing</div>
            </div>
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating...</span>
                </div>
              ) : (
                'Create Schema'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateSchemaModal;