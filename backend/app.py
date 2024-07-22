from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from swagger_config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
swagger = Swagger(app)

# Import and register blueprints
from routes.upload import upload_bp
from routes.execute import execute_bp
from routes.download import download_bp
from routes.analysis import analysis_bp
from routes.status import status_bp
from routes.recent_files import recent_files_bp
from routes.delete import delete_bp
from routes.file_handling import file_header_bp
from routes.dynamic_execute import dynamic_execute_bp

app.register_blueprint(upload_bp)
app.register_blueprint(execute_bp)
app.register_blueprint(download_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(status_bp)
app.register_blueprint(recent_files_bp)
app.register_blueprint(delete_bp)
app.register_blueprint(file_header_bp)
app.register_blueprint(dynamic_execute_bp)

# Run the Flask app
if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    app.run(host="0.0.0.0", port=5000)
