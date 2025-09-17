import React from 'react';
import { useNavigate } from 'react-router-dom';
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
  Container
} from 'lucide-react';
import Layout from '../components/Layout';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const serviceCards = [
    {
      title: 'Database',
      description: 'High-performance managed database service with automatic scaling and built-in analytics.',
      icon: Database,
      action: () => navigate('/schemas'),
      category: 'Database',
      color: 'bg-blue-100 text-blue-600'
    },
    {
      title: 'Vector DB',
      description: 'Specialized vector database for AI applications, embeddings, and similarity search at scale.',
      icon: Brain,
      action: () => console.log('Vector DB clicked'),
      category: 'AI & Vector',
      color: 'bg-purple-100 text-purple-600'
    },
    {
      title: 'Functions',
      description: 'Serverless functions platform for event-driven applications with automatic scaling.',
      icon: Zap,
      action: () => console.log('Functions clicked'),
      category: 'Serverless',
      color: 'bg-yellow-100 text-yellow-600'
    },
    {
      title: 'Virtual Servers',
      description: 'Deploy scalable virtual machines with GPU acceleration for compute-intensive workloads.',
      icon: Server,
      action: () => console.log('Virtual Servers clicked'),
      category: 'Compute',
      color: 'bg-green-100 text-green-600'
    },
    {
      title: 'Kafka',
      description: 'Managed Apache Kafka service for real-time data streaming and event-driven architectures.',
      icon: MessageSquare,
      action: () => console.log('Kafka clicked'),
      category: 'Messaging',
      color: 'bg-orange-100 text-orange-600'
    },
    {
      title: 'Document RAG',
      description: 'Document retrieval and generation system powered by advanced AI for intelligent content processing.',
      icon: FileText,
      action: () => console.log('Document RAG clicked'),
      category: 'AI & ML',
      color: 'bg-indigo-100 text-indigo-600'
    },
    {
      title: 'S3',
      description: 'S3-compatible object storage with enterprise-grade performance, security, and global accessibility.',
      icon: HardDrive,
      action: () => console.log('S3 clicked'),
      category: 'Object Storage',
      color: 'bg-teal-100 text-teal-600'
    },
    {
      title: 'Container Services',
      description: 'Deploy applications using containerized environments with automated scaling and management.',
      icon: Container,
      action: () => console.log('Container Services clicked'),
      category: 'Containers',
      color: 'bg-cyan-100 text-cyan-600'
    }
  ];

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

        {/* Featured Banner */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Power Your AI with Vector DB
              </h3>
              <p className="text-gray-600 mb-4">
                Build intelligent applications with our high-performance vector database. 
                Optimized for embeddings, similarity search, and RAG applications.
              </p>
              <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
                Get Started with Vector DB
              </button>
            </div>
          </div>
        </div>

        {/* Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {serviceCards.map((service, index) => (
            <div
              key={index}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:border-blue-300 hover:shadow-lg transition-all duration-200 cursor-pointer group"
              onClick={service.action}
            >
              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${service.color}`}>
                  <service.icon className="w-6 h-6" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                    {service.category}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                    {service.title}
                  </h3>
                  <p className="text-sm text-gray-600 mt-2 leading-relaxed">
                    {service.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Services</p>
                <p className="text-2xl font-bold text-gray-900">8</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Database Schemas</p>
                <p className="text-2xl font-bold text-gray-900">-</p>
              </div>
              <Database className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="text-lg font-semibold text-green-600">Online</p>
              </div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;