const axios = require('axios');

class VastDbService {
  constructor() {
    this.endpoint = process.env.VAST_ENDPOINT;
    this.accessKeyId = process.env.VAST_ACCESS_KEY_ID;
    this.secretAccessKey = process.env.VAST_SECRET_ACCESS_KEY;
    this.bucketName = process.env.VAST_BUCKET_NAME;
    this.verifySSL = process.env.VAST_VERIFY_SSL !== 'false';
    
    if (!this.endpoint || !this.accessKeyId || !this.secretAccessKey || !this.bucketName) {
      throw new Error('Missing required VAST environment variables');
    }

    this.client = this.createClient();
    this.sessions = new Map(); // Cache database sessions
  }

  createClient() {
    return axios.create({
      baseURL: this.endpoint,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `AWS4-HMAC-SHA256 Credential=${this.accessKeyId}`,
        'X-Amz-Security-Token': this.secretAccessKey
      },
      httpsAgent: !this.verifySSL ? new (require('https').Agent)({
        rejectUnauthorized: false
      }) : undefined
    });
  }

  async connect() {
    try {
      // Test connection to VAST endpoint
      const response = await this.client.get('/health');
      
      return {
        success: true,
        endpoint: this.endpoint,
        bucket: this.bucketName,
        message: 'Connected to VAST Database'
      };
    } catch (error) {
      console.error('VAST DB connection error:', error.message);
      return {
        success: false,
        message: `Failed to connect to VAST Database: ${error.message}`
      };
    }
  }

  async createSchema(schemaName, options = {}) {
    try {
      const sessionKey = `${this.endpoint}:${this.bucketName}:${schemaName}`;
      
      // Simulate vastdb.connect() -> tx.bucket() -> create_schema() pattern
      const transaction = await this.beginTransaction();
      const bucket = transaction.bucket(this.bucketName);
      
      const schema = await bucket.createSchema(schemaName, {
        failIfExists: options.failIfExists !== false,
        ...options
      });

      // Cache the session
      this.sessions.set(sessionKey, {
        schemaName,
        bucket: this.bucketName,
        endpoint: this.endpoint,
        transaction,
        created: Date.now()
      });

      await transaction.commit();

      return {
        success: true,
        schema: {
          name: schemaName,
          bucket: this.bucketName,
          path: `/${this.bucketName}/${schemaName}`,
          protocols: ['DATABASE', 'S3'], // Default protocols for database schemas
          created: new Date().toISOString(),
          id: this.generateSchemaId(schemaName)
        },
        message: `Schema '${schemaName}' created successfully`
      };

    } catch (error) {
      console.error('Create schema error:', error.message);
      return {
        success: false,
        message: error.message
      };
    }
  }

  async listSchemas() {
    try {
      const transaction = await this.beginTransaction();
      const bucket = transaction.bucket(this.bucketName);
      
      const schemas = await bucket.schemas();
      
      const schemaList = schemas.map(schema => ({
        name: schema.name,
        bucket: this.bucketName,
        path: `/${this.bucketName}/${schema.name}`,
        protocols: ['DATABASE', 'S3'],
        created: new Date().toISOString(), // Would come from actual VAST API
        id: this.generateSchemaId(schema.name)
      }));

      await transaction.commit();

      return {
        success: true,
        schemas: schemaList,
        total: schemaList.length
      };

    } catch (error) {
      console.error('List schemas error:', error.message);
      return {
        success: false,
        message: error.message,
        schemas: []
      };
    }
  }

  async getSchema(schemaName) {
    try {
      const transaction = await this.beginTransaction();
      const bucket = transaction.bucket(this.bucketName);
      const schema = await bucket.schema(schemaName, { failIfMissing: false });

      if (!schema) {
        return {
          success: false,
          message: `Schema '${schemaName}' not found`
        };
      }

      // Get tables in this schema
      const tables = await schema.tables();

      await transaction.commit();

      return {
        success: true,
        schema: {
          name: schemaName,
          bucket: this.bucketName,
          path: `/${this.bucketName}/${schemaName}`,
          protocols: ['DATABASE', 'S3'],
          created: new Date().toISOString(),
          id: this.generateSchemaId(schemaName),
          tables: tables.map(table => ({
            name: table.name,
            schema: schemaName,
            columns: table.columns || [],
            rows: table.rowCount || 0,
            created: table.created || new Date().toISOString()
          }))
        }
      };

    } catch (error) {
      console.error('Get schema error:', error.message);
      return {
        success: false,
        message: error.message
      };
    }
  }

  async deleteSchema(schemaName) {
    try {
      const transaction = await this.beginTransaction();
      const bucket = transaction.bucket(this.bucketName);
      const schema = await bucket.schema(schemaName);
      
      await schema.drop();
      await transaction.commit();

      // Clean up cached session
      const sessionKey = `${this.endpoint}:${this.bucketName}:${schemaName}`;
      this.sessions.delete(sessionKey);

      return {
        success: true,
        message: `Schema '${schemaName}' deleted successfully`
      };

    } catch (error) {
      console.error('Delete schema error:', error.message);
      return {
        success: false,
        message: error.message
      };
    }
  }

  async createTable(schemaName, tableName, columns = []) {
    try {
      const transaction = await this.beginTransaction();
      const bucket = transaction.bucket(this.bucketName);
      const schema = await bucket.schema(schemaName);

      // Convert columns to PyArrow-like schema format
      const paSchema = this.convertToPyArrowSchema(columns);
      
      const table = await schema.createTable(tableName, paSchema, {
        failIfExists: false
      });

      await transaction.commit();

      return {
        success: true,
        table: {
          name: tableName,
          schema: schemaName,
          columns: columns,
          created: new Date().toISOString(),
          rows: 0
        },
        message: `Table '${tableName}' created successfully`
      };

    } catch (error) {
      console.error('Create table error:', error.message);
      return {
        success: false,
        message: error.message
      };
    }
  }

  // Helper methods to simulate vastdb transaction pattern
  async beginTransaction() {
    return {
      bucket: (bucketName) => ({
        createSchema: async (schemaName, options = {}) => {
          // Simulate schema creation
          return {
            name: schemaName,
            bucket: bucketName
          };
        },
        schemas: async () => {
          // Return mock schemas for now
          // In real implementation, this would call VAST API
          return [
            { name: 'analytics' },
            { name: 'users' },
            { name: 'events' }
          ];
        },
        schema: async (schemaName, options = {}) => {
          return {
            name: schemaName,
            bucket: bucketName,
            tables: async () => [
              { name: 'users', columns: [], rowCount: 0 },
              { name: 'events', columns: [], rowCount: 0 }
            ],
            createTable: async (tableName, schema, options = {}) => {
              return {
                name: tableName,
                schema: schemaName,
                columns: schema
              };
            },
            drop: async () => {
              // Simulate schema deletion
              return true;
            }
          };
        }
      }),
      commit: async () => {
        // Simulate transaction commit
        return true;
      }
    };
  }

  convertToPyArrowSchema(columns) {
    // Convert JavaScript column definitions to PyArrow-like schema
    return columns.map(col => ({
      name: col.name,
      type: this.mapToArrowType(col.type),
      nullable: col.nullable !== false
    }));
  }

  mapToArrowType(jsType) {
    const typeMap = {
      'string': 'utf8',
      'int': 'int64',
      'integer': 'int64',
      'float': 'float64',
      'double': 'float64',
      'boolean': 'bool',
      'date': 'date32',
      'timestamp': 'timestamp'
    };
    return typeMap[jsType] || 'utf8';
  }

  generateSchemaId(schemaName) {
    // Generate a deterministic ID for the schema
    return Buffer.from(`${this.bucketName}-${schemaName}`).toString('base64').substring(0, 16);
  }

  // Clean up expired sessions
  cleanupSessions() {
    const now = Date.now();
    for (const [key, session] of this.sessions.entries()) {
      const ageHours = (now - session.created) / (1000 * 60 * 60);
      if (ageHours > 8) {
        this.sessions.delete(key);
      }
    }
  }

  getConnectionInfo() {
    return {
      endpoint: this.endpoint,
      bucket: this.bucketName,
      sessionsCount: this.sessions.size,
      connected: true
    };
  }
}

// Cleanup expired sessions every hour
const vastDbService = new VastDbService();
setInterval(() => {
  vastDbService.cleanupSessions();
}, 60 * 60 * 1000);

module.exports = vastDbService;