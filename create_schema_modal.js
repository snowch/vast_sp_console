import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { X, Database } from 'lucide-react';

const CreateSchemaModal = ({ onClose, onCreate, isLoading }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch
  } = useForm({
    defaultValues: {
      name: '',
      path: '',
      protocols: ['DATABASE', 'S3'],
      description: ''
    }
  });

  const watchedName = watch('name');
  const suggestedPath = watchedName ? `/${watchedName.toLowerCase().replace(/[^a-z0-9]/g, '')}` : '';

  const onSubmit = (data) => {
    const schemaData = {
      ...data,
      path: data.path || suggestedPath
    };
    onCreate(schemaData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Database className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Create Schema</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={isLoading}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

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
                  value: /^[a-zA-Z][a-zA-Z0-9_]{0,63}$/,
                  message: 'Name must start with letter, contain only letters, numbers, underscore'
                }
              })}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="my_database"
              disabled={isLoading}
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="path" className="block text-sm font-medium text-gray-700 mb-1">
              Path *
            </label>
            <input
              id="path"
              {...register('path', {
                pattern: {
                  value: /^\/[a-zA-Z0-9_-]+$/,
                  message: 'Path must start with / and contain only letters, numbers, underscore, dash'
                }
              })}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.path ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder={suggestedPath || '/my_database'}
              disabled={isLoading}
            />
            {errors.path && (
              <p className="mt-1 text-sm text-red-600">{errors.path.message}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              Leave empty to auto-generate from schema name
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Protocols *
            </label>
            <div className="space-y-2">
              {['DATABASE', 'S3', 'NFS', 'SMB'].map((protocol) => (
                <label key={protocol} className="flex items-center">
                  <input
                    type="checkbox"
                    value={protocol}
                    {...register('protocols', {
                      required: 'At least one protocol must be selected'
                    })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    disabled={isLoading}
                  />
                  <span className="ml-2 text-sm text-gray-700">{protocol}</span>
                </label>
              ))}
            </div>
            {errors.protocols && (
              <p className="mt-1 text-sm text-red-600">{errors.protocols.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              id="description"
              {...register('description', {
                maxLength: { value: 255, message: 'Description too long (max 255 characters)' }
              })}
              rows={3}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.description ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Optional description for this schema"
              disabled={isLoading}
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
            )}
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Creating...
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