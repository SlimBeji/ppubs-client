from flask import Blueprint, render_template

dashboard_blueprint = Blueprint('Dashboard', __name__)

@dashboard_blueprint.route("/")
def render_dashboard():
    return render_template("dashboard.j2")
