const express = require('express');
const router = express.Router();
const { authenticate, authorize } = require('../middleware/auth');

// Company routes (public)
router.post('/companies', require('./companies').create);
router.get('/companies/:id', require('./companies').get);

// Classification routes (protected)
router.get('/classifications/pending', 
    authenticate, 
    authorize(['analyst', 'admin']), 
    require('./classifications').getPending
);

router.post('/classifications/:id/approve', 
    authenticate, 
    authorize(['analyst', 'admin']), 
    require('./classifications').approve
);

router.post('/classifications/:id/correct', 
    authenticate, 
    authorize(['analyst', 'admin']), 
    require('./classifications').correct
);

// Analytics routes (protected)
router.get('/analytics/performance', 
    authenticate, 
    authorize(['admin']), 
    require('./analytics').getPerformanceMetrics
);

router.get('/analytics/workload', 
    authenticate, 
    authorize(['admin']), 
    require('./analytics').getWorkloadMetrics
);

// Auth routes
router.post('/auth/login', require('./auth').login);
router.post('/auth/refresh', require('./auth').refresh);

// User management (admin only)
router.get('/users', 
    authenticate, 
    authorize(['admin']), 
    require('./users').list
);

router.post('/users', 
    authenticate, 
    authorize(['admin']), 
    require('./users').create
);

module.exports = router;