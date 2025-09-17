import { apiClient } from './apiClient';

class SchemaService {
  async listSchemas() {
    const response = await apiClient.get('/schemas');
    return response.data;
  }

  async createSchema(schemaData) {
    const response = await apiClient.post('/schemas', schemaData);
    return response.data;
  }

  async getSchema(schemaName) {
    const response = await apiClient.get(`/schemas/${schemaName}`);
    return response.data;
  }

  async deleteSchema(schemaName) {
    const response = await apiClient.delete(`/schemas/${schemaName}`);
    return response.data;
  }
}

export const schemaService = new SchemaService();
