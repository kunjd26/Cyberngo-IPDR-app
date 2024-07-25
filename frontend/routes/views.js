import express from 'express';
import axios from 'axios';
import env from './../config/EnvironmentConfig.js';
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

export default router;
