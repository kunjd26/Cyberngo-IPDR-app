import express from 'express';
import axios from 'axios';
import env from './../config/EnvironmentConfig.js';
import globalErrorHandler from './../config/GlobalErrorHandler.js';
import FormData from 'form-data';
const router = express.Router();

// Upload ipdr file.
router.post('/ipdr-file/upload', async function (req, res, next) {
    try {
        if (!req.files) {
            return res.status(400).send('No files were uploaded.');
        }

        // Create a FormData instance
        const form = new FormData();
        form.append('file', req.files.file.data, req.files.file.name);

        // Add headers to the request
        const headers = {
            ...form.getHeaders(), // Add FormData headers
            'Content-Type': 'multipart/form-data' // This is usually automatically set by FormData
        };

        await axios.post(`${env.SERVER_URL}/api/ipdr-files`, form, { headers });

        res.redirect('/');
    } catch (error) {
        if (error.response) {
            globalErrorHandler.notFound(req, res, next);
        } else {
            next(error);
        }
    }
});

// Delete ipdr file.
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

// Execute ipdr file using general parser.
router.get('/ipdr-files/execute-general', function (req, res, next) {
    try {
        // Call the API and handle the response asynchronously
        axios.get(`${env.SERVER_URL}/api/ipdr-files/execute?token=${req.query.file_token}&static_db_only=${req.query.static_db_only}`)
            .catch(error => { });

        setTimeout(() => {
            return res.redirect('/');
        }, 500);

    } catch (error) {
        if (error.response) {
            globalErrorHandler.notFound(req, res, next);
        } else {
            next(error);
        }
    }
});

router.post('/ipdr-files/execute-dynamic', function (req, res, next) {
    try {
        axios.post(`${env.SERVER_URL}/api/ipdr-files/execute/dynamic?token=${req.query.file_token}&static_db_only=${req.query.static_db_only}`, {
            column_mapping: req.body.column_mapping,
        }).catch(error => { });

        return res.redirect('/');

    } catch (error) {
        if (error.response) {
            globalErrorHandler.notFound(req, res, next);
        } else {
            next(error);
        }
    }
});

export default router;
