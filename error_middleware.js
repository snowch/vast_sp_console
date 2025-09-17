const errorHandler = (err, req, res, next) => {
  console.error(`Error ${req.method} ${req.path}:`, err);

  // Default error response
  let status = 500;
  let message = 'Internal server error';
  let details = null;

  // Handle specific error types
  if (err.name === 'ValidationError') {
    status = 400;
    message = 'Validation error';
    details = err.details;
  } else if (err.name === 'UnauthorizedError') {
    status = 401;
    message = 'Unauthorized';
  } else if (err.name === 'ForbiddenError') {
    status = 403;
    message = 'Forbidden';
  } else if (err.name === 'NotFoundError') {
    status = 404;
    message = 'Resource not found';
  } else if (err.name === 'ConflictError') {
    status = 409;
    message = 'Conflict';
  } else if (err.code === 'ECONNREFUSED') {
    status = 502;
    message = 'Cannot connect to VAST server';
  } else if (err.code === 'ENOTFOUND') {
    status = 502;
    message = 'VAST server not found';
  } else if (err.response) {
    // Axios error with response
    status = err.response.status || 500;
    message = err.response.data?.message || err.message;
    details = err.response.data;
  } else if (err.message) {
    message = err.message;
  }

  // Don't expose internal errors in production
  if (process.env.NODE_ENV === 'production' && status === 500) {
    message = 'Internal server error';
    details = null;
  }

  const errorResponse = { error: message };
  if (details) {
    errorResponse.details = details;
  }

  // Add request ID if available
  if (req.id) {
    errorResponse.requestId = req.id;
  }

  res.status(status).json(errorResponse);
};

module.exports = errorHandler;