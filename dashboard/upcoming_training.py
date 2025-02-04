import cloudinary.uploader
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import dashboard_blueprint
from models import UpcomingTraining, Training,db
from redis_client import redisClient


@dashboard_blueprint.route('/upcoming-training', methods=['GET'])
@login_required
def dash_upcoming_training():
    # Check if upcoming_training are cached in Redis
    cached_upcoming_training = redisClient.get('all_upcoming_trainings')
    trainings = Training.query.all()

    if cached_upcoming_training:
        upcoming_trainings = eval(cached_upcoming_training)  # Convert string to list of dictionaries
    else:
        upcoming_trainings = UpcomingTraining.query.all()
        # Cache the result for 10 minutes (600 seconds)
        redisClient.setex('all_upcoming_trainings', 600, str([upTraining.to_dict() for upTraining in upcoming_trainings]))

    return render_template('dash_upcoming_training.html', upcoming_trainings=upcoming_trainings, trainings=trainings)


@dashboard_blueprint.route('/upcoming_training', methods=['POST'])
@login_required
def create_upcoming_training():
    if request.method == 'POST':
        # Retrieve form data
        training_id = request.form.get('training_id')
        start_date = request.form.get('start_date')
        status = request.form.get('status')

        if not (training_id and start_date and status):
            flash('All fields are required.', 'upcoming_training_creation_error')
            return redirect(url_for('dashboard.dash_upcoming_training'))
        
        training = Training.query.get(training_id)
        if not training:
            flash('All fields are required.', 'upcoming_training_creation_error')
            return redirect(url_for('dashboard.dash_upcoming_training'))
        
        upcoming_training = UpcomingTraining(
            training_id=training_id,
            start_date=start_date,
            status=status
        )
        
        # Add to the session and commit to the database
        db.session.add(upcoming_training)
        db.session.commit()

        # Invalidate the cached upcoming_training
        redisClient.delete('all_upcoming_trainings')
        redisClient.delete('all_upcoming_trainings_site')

        flash('Upcoming Training created successfully!', 'upcoming_training_creation_success')
        return redirect(url_for('dashboard.dash_upcoming_training'))


@dashboard_blueprint.route('/upcoming_training/<int:upcoming_training_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_upcoming_training(upcoming_training_id):
    
    upcoming_training = UpcomingTraining.query.get_or_404(upcoming_training_id)
    trainings = Training.query.all()

    if request.method == 'POST':
        upcoming_training.training_id = request.form['training_id']
        upcoming_training.start_date = request.form['start_date']
        upcoming_training.status = request.form['status']

            # Commit the changes to the database
        db.session.commit()

        # Invalidate the cached upcoming_training
        redisClient.delete('all_upcoming_trainings')
        redisClient.delete('all_upcoming_trainings_site')

        flash('Upcoming Training updated successfully!', 'upcoming_training_creation_success')
        return redirect(url_for('dashboard.dash_upcoming_training'))

    return render_template('dash_edit_upcoming_training.html', upcoming_training=upcoming_training, trainings=trainings)


@dashboard_blueprint.route('/upcoming_training/<int:upcoming_training_id>', methods=['GET'])
@login_required
def preview_upcoming_training(upcoming_training_id):
    
    upcoming_training = UpcomingTraining.query.get_or_404(upcoming_training_id)
    
    return render_template('dash_upcoming_training_preview.html', upcoming_training=upcoming_training)