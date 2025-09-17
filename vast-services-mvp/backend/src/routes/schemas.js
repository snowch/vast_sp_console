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
  body('name')
    .isLength({ min: 1, max: 64 })
    .withMessage('Schema name must be 1-64 characters')
    .matches(/^[a-zA-Z][a-zA-Z0-9_]*$/)
    .withMessage('Schema name must start with letter and contain only letters, numbers, and underscores'),
  body('description')
    .optional()
    .isLength({ max: 255 })
    .withMessage('Description too long')
];

const schemaNameValidation = [
  param('name')
    .isLength({ min: 1, max: 64 })
    .withMessage('Invalid schema name')
    .matches(/^[a-zA-Z][a-zA-Z0-9_]*$/)
    .withMessage('Invalid schema name format')
];

const createTableValidation = [
  body('tableName')
    .isLength({ min: 1, max: 64 })
    .withMessage('Table name must be 1-64 characters')
    .matches(/^[a-zA-Z][a-zA-Z0-9_]*$/)
    .withMessage('Table name must start with letter and contain only letters, numbers, and underscores'),
  body('columns')
    .optional()
    .isArray()
    .withMessage('Columns must be an array'),
  body('columns.*.name')
    .optional()
    .isLength({ min: 1 })
    .withMessage('Column name is required'),
  body('columns.*.type')
    .optional()
    .isIn(['string', 'int', 'integer', 'float', 'double', 'boolean', 'date', 'timestamp'])
    .withMessage('Invalid column type')
];

// Connection and info routes
router.get('/connection', schemaController.getConnectionInfo);

// Schema routes
router.get('/', schemaController.listSchemas);
router.post('/', createSchemaValidation, validateRequest, schemaController.createSchema);
router.get('/:name', schemaNameValidation, validateRequest, schemaController.getSchema);
router.delete('/:name', schemaNameValidation, validateRequest, schemaController.deleteSchema);

// Table routes
router.post('/:name/tables', 
  schemaNameValidation.concat(createTableValidation), 
  validateRequest, 
  schemaController.createTable
);
router.get('/:name/tables', schemaNameValidation, validateRequest, schemaController.listTables);

module.exports = router;