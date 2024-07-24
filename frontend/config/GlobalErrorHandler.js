import env from './EnvironmentConfig.js';

class GlobalErrorHandler {

    notFound(req, res, next) {
        res.render('error', { status: 404, message: 'Not found', stack: 'none' });
    }

    internalServerError(err, req, res, next) {
        let statusCode = err.statusCode || 500;
        let errorMessage = env.APP_ENV == 'development' ? err.message : 'Something went wrong.';
        let errorStack = env.APP_ENV == 'development' ? err.stack : "none";

        res.render('error', { status: statusCode, message: errorMessage, stack: errorStack });
    }
}

export default new GlobalErrorHandler();
