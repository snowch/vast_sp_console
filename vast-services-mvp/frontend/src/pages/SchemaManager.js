import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Plus, Database, Calendar, Trash2, Eye, Server, AlertCircle } from 'lucide-react';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import CreateSchemaModal from '../components/CreateSchemaModal';
import { schemaService } from '../services/schemaService';
import toast from 'react-hot-toast';

const SchemaManager = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedSchema, setSelectedSchema] = useState(null);
  const queryClient = useQueryClient();

  // Fetch connection info
  const { data: connectionInfo } = useQuery(
    'connection-info',
    schemaService.getConnectionInfo,
    {
      refetchInterval: 30000, // Refresh every 30 seconds
      onError: (err) => {
        console.error('Failed to fetch connection info:', err);
      }
    }
  );

  // Fetch schemas
  const { data: schemas, isLoading, error } = useQuery(
    'schemas',
    schemaService.listSchemas,
    {
      onError: (err) => {
        console.error('Failed to fetch schemas:', err);
        toast.error('Failed to load schemas');
      }
    }
  );

  // Create schema mutation
  const createMutation = useMutation(schemaService.createSchema, {
    onSuccess: () => {
      queryClient.invalidateQueries('schemas');
      setShowCreateModal(false);
      toast.success('Schema created successfully');
    },
    onError: (err) => {
      console.error('Failed to create schema:', err);
      toast.error(err.response?.data?.message || 'Failed to create schema');
    }
  });

  // Delete schema mutation
  const deleteMutation = useMutation(schemaService.deleteSchema, {
    onSuccess: () => {
      queryClient.invalidateQueries('schemas');
      toast.success('Schema deleted successfully');
    },
    onError: (err) => {
      console.error('Failed to delete schema:', err);
      toast.error(err.response?.data?.message || 'Failed to delete schema');
    }
  });

  const handleCreateSchema = (schemaData) => {
    createMutation.mutate(schemaData);
  };

  const handleDeleteSchema = (schemaName) => {
    if (window.confirm(`Are you sure you want to delete schema "${schemaName}"? This action cannot be undone.`)) {
      deleteMutation.mutate(schemaName);
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <LoadingSpinner message="Loading database schemas..." />
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4">Failed to load schemas</p>
          <button 
            onClick={() => queryClient.invalidateQueries('schemas')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </Layout>
    );
  }

  const isConnected = connectionInfo?.connection?.status === 'connected';

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Database Schemas</h1>
            <p className="text-gray-600">Manage your VAST database schemas and tables</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            disabled={!isConnected}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus className="w-4 h-4" />
            <span>Create Schema</span>
          </button>
        </div>

        {/* Connection Status */}
        {connectionInfo && (
          <div className={`p-4 rounded-lg border ${
            isConnected 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-center space-x-3">
              <Server className={`w-5 h-5 ${
                isConnected ? 'text-green-600' : 'text-red-600'
              }`} />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-gray-900">VAST Database Connection</span>
                  <div className={`w-2 h-2 rounded-full ${
                    isConnected ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  <strong>Endpoint:</strong> {connectionInfo.connection?.endpoint} | 
                  <strong> Bucket:</strong> {connectionInfo.connection?.bucket}
                </div>
              </div>
              {!isConnected && (
                <button
                  onClick={() => queryClient.invalidateQueries('connection-info')}
                  className="text-sm text-red-600 hover:text-red-800"
                >
                  Retry Connection
                </button>
              )}
            </div>
          </div>
        )}

        {/* Schema Grid */}
        {schemas?.schemas?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {schemas.schemas.map((schema) => (
              <div
                key={schema.id}
                className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Database className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{schema.name}</h3>
                      <p className="text-sm text-gray-500">{schema.path}</p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setSelectedSchema(schema)}
                      className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="View Details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteSchema(schema.name)}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete Schema"
                      disabled={deleteMutation.isLoading}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Protocols:</span>
                    <div className="flex space-x-1">
                      {schema.protocols?.map((protocol) => (
                        <span
                          key={protocol}
                          className={`px-2 py-1 rounded text-xs ${
                            protocol === 'DATABASE' 
                              ? 'bg-blue-100 text-blue-700' 
                              : 'bg-gray-100 text-gray-700'
                          }`}
                        >
                          {protocol}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  {schema.created && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Created:</span>
                      <div className="flex items-center space-x-1 text-gray-500">
                        <Calendar className="w-3 h-3" />
                        <span>{new Date(schema.created).toLocaleDateString()}</span>
                      </div>
                    </div>
                  )}

                  <div className="pt-3 border-t border-gray-100">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Tables:</span>
                      <span className="text-sm font-medium text-gray-900">
                        {schema.tables?.length || 0}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No schemas found</h3>
            <p className="text-gray-600 mb-6">
              {isConnected 
                ? 'Create your first database schema to get started'
                : 'Connect to VAST Database to manage schemas'
              }
            </p>
            {isConnected && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Schema
              </button>
            )}
          </div>
        )}

        {/* Stats Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 pt-6 border-t border-gray-200">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{schemas?.schemas?.length || 0}</p>
            <p className="text-sm text-gray-600">Total Schemas</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">
              {schemas?.schemas?.reduce((acc, schema) => acc + (schema.tables?.length || 0), 0) || 0}
            </p>
            <p className="text-sm text-gray-600">Total Tables</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{connectionInfo?.connection?.bucket || '-'}</p>
            <p className="text-sm text-gray-600">Active Bucket</p>
          </div>
          <div className="text-center">
            <p className={`text-2xl font-bold ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
              {isConnected ? 'Online' : 'Offline'}
            </p>
            <p className="text-sm text-gray-600">Database Status</p>
          </div>
        </div>
      </div>

      {/* Create Schema Modal */}
      {showCreateModal && (
        <CreateSchemaModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateSchema}
          isLoading={createMutation.isLoading}
          connectionInfo={connectionInfo?.connection}
        />
      )}

      {/* Schema Details Modal */}
      {selectedSchema && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Schema Details</h3>
              <button
                onClick={() => setSelectedSchema(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <p className="mt-1 text-sm text-gray-900">{selectedSchema.name}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Path</label>
                <p className="mt-1 text-sm text-gray-900">{selectedSchema.path}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Bucket</label>
                <p className="mt-1 text-sm text-gray-900">{selectedSchema.bucket}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Protocols</label>
                <div className="mt-1 flex space-x-2">
                  {selectedSchema.protocols?.map((protocol) => (
                    <span
                      key={protocol}
                      className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm"
                    >
                      {protocol}
                    </span>
                  ))}
                </div>
              </div>

              {selectedSchema.tables && selectedSchema.tables.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tables</label>
                  <div className="mt-1 space-y-2">
                    {selectedSchema.tables.map((table, index) => (
                      <div key={index} className="text-sm text-gray-900 flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span>• {table.name || table}</span>
                        {table.rows !== undefined && (
                          <span className="text-xs text-gray-500">{table.rows} rows</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default SchemaManager;