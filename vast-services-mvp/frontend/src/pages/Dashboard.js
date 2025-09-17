import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { useAuth } from '../hooks/useAuth';
import { 
  Database, 
  Server, 
  MessageSquare, 
  BarChart3, 
  Settings, 
  LogOut, 
  Brain,
  FileText,
  Zap,
  HardDrive,
  Container,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import Layout from '../components/Layout';
import { schemaService } from '../services/schemaService';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // Fetch connection info and schemas for dashboard stats
  const { data: connectionInfo } = useQuery(
    'connection-info',
    schemaService.getConnectionInfo,
    { refetchInterval: 30000 }
  );

  const { data: schemas } = useQuery(
    'schemas',
    schemaService.listSchemas
  );

  const serviceCards = [
    {
      title: 'Database',
      description: 'High-performance managed database service with automatic scaling and built-in analytics.',
      icon: Database,
      action: () => navigate('/schemas'),
      category: 'Database',
      color: 'bg-blue-100 text-blue-600',
      available: true
    },
    {
      title: 'Vector DB',
      description: 'Specialized vector database for AI applications, embeddings, and similarity search at scale.',
      icon: Brain,
      action: () => console.log('Vector DB clicked'),
      category: 'AI & Vector',
      color: 'bg-purple-100 text-purple-600',
      available: false
    },
    {
      title: 'Functions',
      description: 'Serverless functions platform for event-driven applications with automatic scaling.',
      icon: Zap,
      action: () => console.log('Functions clicked'),
      category: 'Serverless',
      color: 'bg-yellow-100 text-yellow-600',
      available: false
    },
    {
      title: 'Virtual Servers',
      description: 'Deploy scalable virtual machines with GPU acceleration for compute-intensive workloads.',
      icon: Server,
      action: () => console.log('Virtual Servers clicked'),
      category: 'Compute',
      color: 'bg-green-100 text-green-600',
      available: false
    },
    {
      title: 'Event Streaming (Kafka API)',
      description: 'Managed Apache Kafka API for real-time data streaming and event-driven architectures.',
      icon: MessageSquare,
      action: () => console.log('Kafka clicked'),
      category: 'Messaging',
      color: 'bg-orange-100 text-orange-600',
      available: false
    },
    {
      title: 'Document RAG',
      description: 'Document retrieval and generation system powered by advanced AI for intelligent content processing.',
      icon: FileText,
      action: () => console.log('Document RAG clicked'),
      category: 'AI & ML',
      color: 'bg-indigo-100 text-indigo-600',
      available: false
    },
    {
      title: 'S3',
      description: 'S3-compatible object storage with enterprise-grade performance, security, and global accessibility.',
      icon: HardDrive,
      action: () => console.log('S3 clicked'),
      category: 'Object Storage',
      color: 'bg-teal-100 text-teal-600',
      available: false
    },
    {
      title: 'Container Services',
      description: 'Deploy applications using containerized environments with automated scaling and management.',
      icon: Container,
      action: () => console.log('Container Services clicked'),
      category: 'Containers',
      color: 'bg-cyan-100 text-cyan-600',
      available: false
    }
  ];

  const isConnected = connectionInfo?.connection?.status === 'connected';

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-6 text-white">
          <h1 className="text-2xl font-bold mb-2">Welcome to VAST Cloud</h1>
          <p className="text-blue-100">
            Connected to {user?.vastHost} as {user?.username} | Tenant: {user?.tenant}
          </p>
        </div>

        {/* VAST Database Connection Status */}
        {connectionInfo && (
          <div className={`rounded-lg border p-6 ${
            isConnected 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-center space-x-4">
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                isConnected ? 'bg-green-100' : 'bg-red-100'
              }`}>
                {isConnected ? (
                  <CheckCircle className="w-6 h-6 text-green-600" />
                ) : (
                  <AlertCircle className="w-6 h-6 text-red-600" />
                )}
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  VAST Database Connection
                </h3>
                <div className="text-sm text-gray-600 space-y-1">
                  <div><strong>Endpoint:</strong> {connectionInfo.connection?.endpoint}</div>
                  <div><strong>Bucket:</strong> {connectionInfo.connection?.bucket}</div>
                  <div className="flex items-center space-x-2">
                    <strong>Status:</strong>
                    <div className={`w-2 h-2 rounded-full ${
                      isConnected ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
                  </div>
                </div>
                {isConnected && (
                  <button
                    onClick={() => navigate('/schemas')}
                    className="mt-3 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm"
                  >
                    Manage Database Schemas
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Featured Banner */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Database className="w-6 h-6 text-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                VAST Database - Ready to Use
              </h3>
              <p className="text-gray-600 mb-4">
                Create database schemas and tables using the VAST Database service. 
                Your connection is configured via environment variables for seamless access.
              </p>
              <button 
                onClick={() => navigate('/schemas')}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                disabled={!isConnected}
              >
                {isConnected ? 'Get Started with Database' : 'Database Connection Required'}
              </button>
            </div>
          </div>
        </div>

        {/* Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {serviceCards.map((service, index) => (
            <div
              key={index}
              className={`bg-white rounded-lg border border-gray-200 p-6 transition-all duration-200 cursor-pointer group ${
                service.available 
                  ? 'hover:border-blue-300 hover:shadow-lg' 
                  : 'opacity-60 cursor-not-allowed'
              }`}
              onClick={service.available ? service.action : undefined}
            >
              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${service.color}`}>
                  <service.icon className="w-6 h-6" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <div className="text-xs text-gray-500 uppercase tracking-wide">
                      {service.category}
                    </div>
                    {service.available && (
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    )}
                  </div>
                  <h3 className={`text-lg font-semibold text-gray-900 transition-colors ${
                    service.available ? 'group-hover:text-blue-600' : ''
                  }`}>
                    {service.title}
                  </h3>
                  <p className="text-sm text-gray-600 mt-2 leading-relaxed">
                    {service.description}
                  </p>
                  {!service.available && (
                    <p className="text-xs text-gray-400 mt-2 italic">Coming Soon</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Available Services</p>
                <p className="text-2xl font-bold text-gray-900">
                  {serviceCards.filter(s => s.available).length}
                </p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Database Schemas</p>
                <p className="text-2xl font-bold text-gray-900">
                  {schemas?.schemas?.length || 0}
                </p>
              </div>
              <Database className="w-8 h-8 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Bucket</p>
                <p className="text-lg font-semibold text-gray-900">
                  {connectionInfo?.connection?.bucket || '-'}
                </p>
              </div>
              <HardDrive className="w-8 h-8 text-purple-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Database Status</p>
                <p className={`text-lg font-semibold ${
                  isConnected ? 'text-green-600' : 'text-red-600'
                }`}>
                  {isConnected ? 'Online' : 'Offline'}
                </p>
              </div>
              <div className={`w-3 h-3 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;