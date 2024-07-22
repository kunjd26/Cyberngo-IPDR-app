class Config:
    DEBUG = True
    SWAGGER = {
        "title": "My API",
        "uiversion": 3,
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/api/docs/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/api/docs/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/",
    }
