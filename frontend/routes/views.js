import express from 'express';
import axios from 'axios';
import env from './../config/EnvironmentConfig.js';
import globalErrorHandler from './../config/GlobalErrorHandler.js';
const router = express.Router();

router.get('/', async function (req, res, next) {
    try {
        const response = await axios.get(`${env.SERVER_URL}/api/ipdr-files?n=100`);
        const data = response.data.data;
        return res.render('index', { data });
    } catch (error) {
        if (error.response) {
            return res.render('index', { data: [] });
        } else {
            next(error);
        }
    }
});

router.get('/ipdr-files/delete', async function (req, res, next) {
    try {
        await axios.delete(`${env.SERVER_URL}/api/ipdr-files?token=${req.query.file_token}`);
        return res.redirect('/');
    } catch (error) {
        if (error.response) {
            globalErrorHandler.notFound(req, res, next);
        } else {
            next(error);
        }
    }
});

router.get('/ipdr-files/execute', function (req, res, next) {
    try {
        axios.get(`${env.SERVER_URL}/api/ipdr-files/execute?token=${req.query.file_token}`);
        return res.redirect('/');
    } catch (error) {
        if (error.response) {
            globalErrorHandler.notFound(req, res, next);
        } else {
            next(error);
        }
    }
});

router.post('/upload', function (req, res, next) {
    try {
        console.log(req.files);
        res.redirect('/');
    } catch (error) {
        if (error.response) {
            globalErrorHandler.notFound(req, res, next);
        } else {
            next(error);
        }
    }
});

export default router;
