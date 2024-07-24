import 'dotenv/config'

const environmentConfig = {
    APP_ENV: process.env.APP_ENV,
    APP_HOST: process.env.APP_HOST,
    APP_PORT: process.env.APP_PORT,
    APP_URL: `${process.env.APP_HOST}:${process.env.APP_PORT}`,

    SERVER_HOST: process.env.SERVER_HOST,
    SERVER_PORT: process.env.SERVER_PORT,
    SERVER_URL: `${process.env.SERVER_HOST}:${process.env.SERVER_PORT}`,
}

const env = Object.freeze(environmentConfig);

export default env;
