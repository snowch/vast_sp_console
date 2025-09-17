const express = require('express');
const { body } = require('express-validator');
const authController = require('../controllers/authController');
const validateRequest = require('../middleware/validateRequest');

const router = express.Router();

// Validation rules
const loginValidation = [
  body('vastHost').isIP().withMessage('Invalid VAST host IP address'),
  body('vastPort').isInt({ min: 1, max: 65535 }).withMessage('Invalid port number'),
  body('username').isLength({ min: 1 }).withMessage('Username is required'),
  body('password').isLength({ min: 1 }).withMessage('Password is required'),
  body('tenant').optional().isLength({ min: 1 }).withMessage('Tenant name cannot be empty')
];

// Routes
router.post('/login', loginValidation, validateRequest, authController.login);
router.post('/logout', authController.logout);
router.get('/verify', authController.verifyToken);

module.exports = router;