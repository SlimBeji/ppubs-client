import os


class Config(object):
    __skip_field_verification = []

    @classmethod
    def check_missing_parameters(cls):
        missing_parameters = []
        for variable, value in cls.__dict__.items():
            if (
                not variable.startswith("__")
                and variable not in cls.__skip_field_verification
            ):
                if value is None:
                    missing_parameters.append(variable)

        if missing_parameters:
            raise Exception(
                "The following environment variables are missing: %r"
                % missing_parameters
            )

    # App config section
    PORT = os.getenv("PORT", 5000)
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    SECRET_KEY = os.getenv("FLASK_SECRET", "Secret")

    APP_DIR = os.path.dirname(__file__)
    ROOT_DIR = os.path.dirname(APP_DIR)

    # Swagger and Redoc section
    API_TITLE = "Ppubs client"
    API_VERSION = "0.1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/spec"
    OPENAPI_JSON_PATH = "api-spec.json"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = (
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


# Checking if some environment variables are not set
Config.check_missing_parameters()
