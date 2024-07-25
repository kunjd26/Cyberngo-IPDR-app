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

router.get('/ipdr-header/:uuid', async function (req, res, next) {
    try {
        const static_db_only = req.query.static_db_only ?? false;
        const response = await axios.get(`${env.SERVER_URL}/api/ipdr-files/header?token=${req.params.uuid}&static_db_only=${static_db_only}`);
        const data = response.data.data;
        return res.render('ipdr-header', { data, file_token: req.params.uuid, static_db_only });
    } catch (error) {
        if (error.response) {
            globalErrorHandler.notFound(req, res, next);
        } else {
            next(error);
        }
    }
});

export default router;
