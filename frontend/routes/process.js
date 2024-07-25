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
        axios.get(`${env.SERVER_URL}/api/ipdr-files/execute?token=${req.query.file_token}&static_db_only=${req.query.static_db_only}`);

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

router.post('/ipdr-files/execute-dynamic', async function (req, res, next) {
    try {
        console.log("CP:00");

        const response = await axios.post(`${env.SERVER_URL}/api/ipdr-files/execute-dynamic?token=${req.query.file_token}&static_db_only=${req.query.static_db_only}`, {
            column_mapping: req.body.column_mapping,
        });

        console.log("CP:01", response.data); // Log the response data to ensure the request was successful

        return res.redirect('/');
    } catch (error) {
        console.error("Error occurred:", error); // Log the error message

        if (error.response) {
            globalErrorHandler.notFound(req, res, next);
        } else {
            next(error);
        }
    }
});

export default router;
