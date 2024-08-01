FROM node:20.10-alpine
WORKDIR /app
COPY package.json .
RUN npm install
ENV APP_ENV=development \
    APP_PORT=3000 \
    APP_HOST=http://127.0.0.1 \
    SERVER_PORT=5000 \
    SERVER_HOST=http://127.0.0.1
COPY . .
EXPOSE 3000
ENTRYPOINT [ "node", "app.js"]