from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import dashboard_blueprint
from models import ContactUs, db
from redis_client import redisClient


@dashboard_blueprint.route('/user-feedback')
@login_required
def dash_user_feedback():
    # Check if trainings are cached in Redis
    cached_feedbacks = redisClient.get('all_feedback')

    if cached_feedbacks:
        feedbacks = eval(cached_feedbacks)  # Convert string to list of dictionaries
    else:
        feedbacks = ContactUs.query.all()
        # Cache the result for 10 minutes (600 seconds)
        redisClient.setex('all_feedbacks', 600, str([training.to_dict() for training in feedbacks]))

    return render_template('dash_feedbacks.html', feedbacks=feedbacks)