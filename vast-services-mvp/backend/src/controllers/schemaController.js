const vastService = require('../services/vastService');
const databaseService = require('../services/databaseService');

class SchemaController {
  async listSchemas(req, res, next) {
    try {
      const { vastHost, vastPort, tenant } = req.user;
      
      // Get existing views that can serve as schemas
      const viewsResult = await vastService.getViews(vastHost, vastPort, tenant);
      
      if (!viewsResult.success) {
        return res.status(500).json({ 
          error: 'Failed to fetch schemas',
          message: viewsResult.message 
        });
      }

      // Filter for database-enabled views
      const schemas = viewsResult.data.results ? viewsResult.data.results
        .filter(view => view.protocols && view.protocols.includes('DATABASE'))
        .map(view => ({
          name: view.bucket,
          path: view.path,
          protocols: view.protocols,
          created: view.created,
          id: view.id
        })) : [];

      res.json({
        success: true,
        schemas,
        total: schemas.length
      });

    } catch (error) {
      console.error('List schemas error:', error);
      next(error);
    }
  }

  async createSchema(req, res, next) {
    try {
      const { name, path, protocols, description } = req.body;
      const { vastHost, vastPort, tenant, username } = req.user;

      // Prepare view data for VAST API
      const viewData = {
        path,
        bucket: name,
        bucket_owner: username,
        protocols: protocols || ['S3', 'DATABASE'],
        create_dir: true,
        policy_id: 1 // Default policy - should be fetched dynamically
      };

      // Create the view which serves as our schema
      const createResult = await vastService.createView(vastHost, vastPort, tenant, viewData);
      
      if (!createResult.success) {
        return res.status(400).json({
          error: 'Failed to create schema',
          message: createResult.message
        });
      }

      // Initialize database connection for this schema
      try {
        await databaseService.initializeSchema({
          vastHost,
          vastPort,
          username,
          tenant,
          bucketName: name
        });
      } catch (dbError) {
        console.warn('Database initialization failed (this is normal for new schemas):', dbError.message);
      }

      res.status(201).json({
        success: true,
        schema: {
          name,
          path,
          protocols: viewData.protocols,
          id: createResult.data.id
        },
        message: 'Schema created successfully'
      });

    } catch (error) {
      console.error('Create schema error:', error);
      next(error);
    }
  }

  async getSchema(req, res, next) {
    try {
      const { name } = req.params;
      const { vastHost, vastPort, tenant } = req.user;

      const viewsResult = await vastService.getViews(vastHost, vastPort, tenant);
      
      if (!viewsResult.success) {
        return res.status(500).json({ 
          error: 'Failed to fetch schema',
          message: viewsResult.message 
        });
      }

      const schema = viewsResult.data.results ? viewsResult.data.results
        .find(view => view.bucket === name && view.protocols.includes('DATABASE')) : null;

      if (!schema) {
        return res.status(404).json({ 
          error: 'Schema not found',
          message: `Schema '${name}' does not exist` 
        });
      }

      // Get database information if available
      let tables = [];
      try {
        const tablesList = await databaseService.listTables({
          vastHost,
          vastPort,
          tenant,
          bucketName: name
        });
        tables = tablesList.tables || [];
      } catch (dbError) {
        console.warn('Failed to fetch tables:', dbError.message);
      }

      res.json({
        success: true,
        schema: {
          name: schema.bucket,
          path: schema.path,
          protocols: schema.protocols,
          created: schema.created,
          id: schema.id,
          tables
        }
      });

    } catch (error) {
      console.error('Get schema error:', error);
      next(error);
    }
  }

  async deleteSchema(req, res, next) {
    try {
      const { name } = req.params;
      
      // In a real implementation, we'd delete the view via VAST API
      // For now, return a placeholder response
      res.json({
        success: true,
        message: `Schema '${name}' deletion initiated`,
        note: 'Schema deletion requires additional VAST API endpoints'
      });

    } catch (error) {
      console.error('Delete schema error:', error);
      next(error);
    }
  }

  async createTable(req, res, next) {
    try {
      const { name: schemaName } = req.params;
      const { tableName, columns } = req.body;
      const { vastHost, vastPort, tenant, username } = req.user;

      const result = await databaseService.createTable({
        vastHost,
        vastPort,
        tenant,
        bucketName: schemaName,
        tableName,
        columns: columns || []
      });

      if (!result.success) {
        return res.status(400).json({
          error: 'Failed to create table',
          message: result.message
        });
      }

      res.status(201).json({
        success: true,
        table: result.table,
        message: `Table '${tableName}' created successfully`
      });

    } catch (error) {
      console.error('Create table error:', error);
      next(error);
    }
  }

  async listTables(req, res, next) {
    try {
      const { name: schemaName } = req.params;
      const { vastHost, vastPort, tenant } = req.user;

      const result = await databaseService.listTables({
        vastHost,
        vastPort,
        tenant,
        bucketName: schemaName
      });

      res.json({
        success: true,
        tables: result.tables || [],
        schema: schemaName
      });

    } catch (error) {
      console.error('List tables error:', error);
      next(error);
    }
  }
}

module.exports = new SchemaController();