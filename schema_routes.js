const express = require('express');
const { body, param } = require('express-validator');
const schemaController = require('../controllers/schemaController');
const authenticateToken = require('../middleware/authenticateToken');
const validateRequest = require('../middleware/validateRequest');

const router = express.Router();

// All schema routes require authentication
router.use(authenticateToken);

// Validation rules
const createSchemaValidation = [
  body('name').isLength({ min: 1, max: 64 }).withMessage('Schema name must be 1-64 characters'),
  body('path').matches(/^\/[a-zA-Z0-9_-]+$/).withMessage('Path must start with / and contain only alphanumeric, _ or - characters'),
  body('protocols').isArray({ min: 1 }).withMessage('At least one protocol must be specified'),
  body('protocols.*').isIn(['NFS', 'SMB', 'S3', 'DATABASE', 'KAFKA']).withMessage('Invalid protocol'),
  body('description').optional().isLength({ max: 255 }).withMessage('Description too long')
];

const schemaNameValidation = [
  param('name').isLength({ min: 1, max: 64 }).withMessage('Invalid schema name')
];

// Routes
router.get('/', schemaController.listSchemas);
router.post('/', createSchemaValidation, validateRequest, schemaController.createSchema);
router.get('/:name', schemaNameValidation, validateRequest, schemaController.getSchema);
router.delete('/:name', schemaNameValidation, validateRequest, schemaController.deleteSchema);

// Database-specific routes
router.post('/:name/tables', schemaNameValidation, validateRequest, schemaController.createTable);
router.get('/:name/tables', schemaNameValidation, validateRequest, schemaController.listTables);

module.exports = router;