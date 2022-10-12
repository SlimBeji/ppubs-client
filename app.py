from flask import Flask

from extensions import api, ma
from api import api_blueprints
from views import views_blueprint


def register_extensions(app):
    api.init_app(app)
    ma.init_app(app)


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    register_extensions(app)
    
    for api_blueprint in api_blueprints:
        api.register_blueprint(api_blueprint)

    for view_blueprint in views_blueprint:
        app.register_blueprint(view_blueprint)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=app.config.get("PORT"))
