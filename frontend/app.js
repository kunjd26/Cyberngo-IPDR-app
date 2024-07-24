import express from 'express';
import path from 'path';
import cookieParser from 'cookie-parser';
import logger from 'morgan';
import { dirname } from 'path';
import { fileURLToPath } from 'url';
import cors from 'cors';
import ejs from "ejs";

// Local imports.
import viewRouter from './routes/views.js';
import globalErrorHandler from './config/GlobalErrorHandler.js';
import env from './config/EnvironmentConfig.js';

// Initialize.
export const app = express();
const __dirname = dirname(fileURLToPath(import.meta.url));

// Global middlewares.
app.use(cors());
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// view engine setup.
app.set('views', path.join(__dirname, 'views'));
app.engine('.html', ejs.renderFile);
app.set('view engine', 'html');

// Routes.
app.use('/', viewRouter);

// Global error handler middlewares.
app.use(globalErrorHandler.notFound);
app.use(globalErrorHandler.internalServerError);

const PORT = env.APP_PORT || 3000;
const APP_URL = env.APP_URL;

app.listen(PORT, () => {
  console.log(`Server running at ${APP_URL}.`);
});

export default app;
