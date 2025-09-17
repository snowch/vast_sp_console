const vastDbService = require('../services/vastDbService');

class SchemaController {
  async listSchemas(req, res, next) {
    try {
      const result = await vastDbService.listSchemas();
      
      if (!result.success) {
        return res.status(500).json({ 
          error: 'Failed to fetch schemas',
          message: result.message 
        });
      }

      res.json({
        success: true,
        schemas: result.schemas,
        total: result.total,
        connection: vastDbService.getConnectionInfo()
      });

    } catch (error) {
      console.error('List schemas error:', error);
      next(error);
    }
  }

  async createSchema(req, res, next) {
    try {
      const { name, description } = req.body;

      if (!name) {
        return res.status(400).json({
          error: 'Schema name is required'
        });
      }

      // Validate schema name
      if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(name)) {
        return res.status(400).json({
          error: 'Invalid schema name. Must start with letter and contain only letters, numbers, and underscores.'
        });
      }

      const result = await vastDbService.createSchema(name, {
        description,
        failIfExists: true
      });
      
      if (!result.success) {
        return res.status(400).json({
          error: 'Failed to create schema',
          message: result.message
        });
      }

      res.status(201).json({
        success: true,
        schema: result.schema,
        message: result.message
      });

    } catch (error) {
      console.error('Create schema error:', error);
      next(error);
    }
  }

  async getSchema(req, res, next) {
    try {
      const { name } = req.params;

      const result = await vastDbService.getSchema(name);
      
      if (!result.success) {
        return res.status(404).json({ 
          error: 'Schema not found',
          message: result.message 
        });
      }

      res.json({
        success: true,
        schema: result.schema
      });

    } catch (error) {
      console.error('Get schema error:', error);
      next(error);
    }
  }

  async deleteSchema(req, res, next) {
    try {
      const { name } = req.params;
      
      const result = await vastDbService.deleteSchema(name);
      
      if (!result.success) {
        return res.status(400).json({
          error: 'Failed to delete schema',
          message: result.message
        });
      }

      res.json({
        success: true,
        message: result.message
      });

    } catch (error) {
      console.error('Delete schema error:', error);
      next(error);
    }
  }

  async createTable(req, res, next) {
    try {
      const { name: schemaName } = req.params;
      const { tableName, columns = [] } = req.body;

      if (!tableName) {
        return res.status(400).json({
          error: 'Table name is required'
        });
      }

      // Default columns if none provided
      const defaultColumns = columns.length > 0 ? columns : [
        { name: 'id', type: 'int64', nullable: false },
        { name: 'created_at', type: 'timestamp', nullable: false },
        { name: 'updated_at', type: 'timestamp', nullable: true }
      ];

      const result = await vastDbService.createTable(schemaName, tableName, defaultColumns);

      if (!result.success) {
        return res.status(400).json({
          error: 'Failed to create table',
          message: result.message
        });
      }

      res.status(201).json({
        success: true,
        table: result.table,
        message: result.message
      });

    } catch (error) {
      console.error('Create table error:', error);
      next(error);
    }
  }

  async listTables(req, res, next) {
    try {
      const { name: schemaName } = req.params;

      const result = await vastDbService.getSchema(schemaName);

      if (!result.success) {
        return res.status(404).json({
          error: 'Schema not found',
          message: result.message
        });
      }

      res.json({
        success: true,
        tables: result.schema.tables || [],
        schema: schemaName
      });

    } catch (error) {
      console.error('List tables error:', error);
      next(error);
    }
  }

  async getConnectionInfo(req, res, next) {
    try {
      const connectionInfo = vastDbService.getConnectionInfo();
      const connectionTest = await vastDbService.connect();

      res.json({
        success: true,
        connection: {
          ...connectionInfo,
          status: connectionTest.success ? 'connected' : 'disconnected',
          message: connectionTest.message
        }
      });

    } catch (error) {
      console.error('Get connection info error:', error);
      next(error);
    }
  }
}

module.exports = new SchemaController();