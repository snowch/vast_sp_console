import { apiClient } from './apiClient';

class SchemaService {
  async getConnectionInfo() {
    const response = await apiClient.get('/database/schemas/connection');
    return response.data;
  }

  async listSchemas() {
    const response = await apiClient.get('/database/schemas');
    return response.data;
  }

  async createSchema(schemaData) {
    const response = await apiClient.post('/database/schemas', {
      name: schemaData.name,
      description: schemaData.description
    });
    return response.data;
  }

  async getSchema(schemaName) {
    const response = await apiClient.get(`/database/schemas/${schemaName}`);
    return response.data;
  }

  async deleteSchema(schemaName) {
    const response = await apiClient.delete(`/database/schemas/${schemaName}`);
    return response.data;
  }

  async createTable(schemaName, tableData) {
    const response = await apiClient.post(`/database/schemas/${schemaName}/tables`, tableData);
    return response.data;
  }

  async listTables(schemaName) {
    const response = await apiClient.get(`/database/schemas/${schemaName}/tables`);
    return response.data;
  }

  // Health check for database schemas service
  async healthCheck() {
    const response = await apiClient.get('/database/schemas/health');
    return response.data;
  }
}

export const schemaService = new SchemaService();