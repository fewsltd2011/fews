from flask import Blueprint, render_template

# Define the blueprint and set the template folder
dashboard_blueprint = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static', static_url_path='assets')

# Import routes after defining the blueprint
from . import dashboard
from . import authentication
from . import user
from . import projects
from . import trainings
from . import news
from . import userFeedback
from . import upcoming_training
