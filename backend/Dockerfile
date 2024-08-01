FROM python:3.12-alpine
WORKDIR /app
COPY cyberngo.db .
RUN pip install flask==3.0.3 flask_cors==4.0.1 ipaddress ipinfo==5.0.1 pandas==2.2.2 uuid flasgger==0.9.7.1
RUN mkdir -p /app/files && chmod -R 777 /app/files
COPY . .
EXPOSE 5000
ENTRYPOINT [ "python", "app.py"]