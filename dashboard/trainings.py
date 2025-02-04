from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import dashboard_blueprint
from models import Training, db
from redis_client import redisClient


@dashboard_blueprint.route('/trainings', methods=['GET'])
@login_required
def dash_training_catalog():
    # Check if trainings are cached in Redis
    cached_trainings = redisClient.get('all_trainings')

    if cached_trainings:
        trainings = eval(cached_trainings)  # Convert string to list of dictionaries
    else:
        trainings = Training.query.all()
        # Cache the result for 10 minutes (600 seconds)
        redisClient.setex('all_trainings', 600, str([training.to_dict() for training in trainings]))

    return render_template('dash_trainings.html', trainings=trainings)


@dashboard_blueprint.route('/trainings', methods=['POST'])
@login_required
def create_training():
    if request.method == 'POST':
        # Retrieve form data
        title = request.form.get('title')
        desc = request.form.get('desc')
        number_of_cpds = request.form.get('number_of_cpds')
        content = request.form.get('content')
        type = request.form.get('type')
        duration = request.form.get('duration')
        daily_schedule = request.form.get('daily_schedule')
        training_style = request.form.get('training_style')
        online_knowledge_test = request.form.get('online_knowledge_test')
        certification = request.form.get('certification')
        instructor = request.form.get('instructor')
        fees = request.form.get('fees')

        # Validate form data
        if not (title and desc and number_of_cpds and content and type and duration and daily_schedule and training_style and online_knowledge_test and certification and instructor and fees):
            flash('All fields are required.', 'training_creation_error')
            return redirect(url_for('dashboard.dash_training_catalog'))


        # Create a new training and add it to the database
        new_training = Training(
            title=title,  # Use the uploaded image URL
            desc=desc,
            number_of_cpds=number_of_cpds,
            content=content,
            type=type,
            duration=duration,
            daily_schedule=daily_schedule,
            training_style=training_style,
            online_knowledge_test=online_knowledge_test,
            certification=certification,
            instructor=instructor,
            fees=fees
        )
        db.session.add(new_training)
        db.session.commit()

        # Invalidate the cached trainings
        redisClient.delete('all_trainings')
        redisClient.delete('latest_trainings')

        flash('training created successfully!', 'training_creation_success')
        return redirect(url_for('dashboard.dash_training_catalog'))


@dashboard_blueprint.route('/trainings/<int:training_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_training(training_id):
    training = Training.query.get_or_404(training_id)

    if request.method == 'POST':
        training.title = request.form['title']
        training.desc = request.form['desc']
        training.number_of_cpds = request.form['number_of_cpds']
        training.content = request.form['content']
        training.type = request.form['type']
        training.duration = request.form['duration']
        training.daily_schedule = request.form['daily_schedule']
        training.training_style = request.form['training_style']
        training.online_knowledge_test = request.form['online_knowledge_test']
        training.certification = request.form['certification']
        training.instructor = request.form['instructor']
        training.fees = request.form['fees']
        
        
        # Commit the changes to the database
        db.session.commit()

        # Invalidate the cached trainings
        redisClient.delete('all_trainings')
        redisClient.delete('latest_trainings')

        flash('training updated successfully!', 'training_creation_success')
        return redirect(url_for('dashboard.dash_training_catalog'))

    return render_template('dash_edit_training.html', training=training)


@dashboard_blueprint.route('/trainings/<int:training_id>', methods=['GET'])
@login_required
def preview_training(training_id):
    
    training = Training.query.get_or_404(training_id)

    return render_template('dash_training_preview.html', training=training)


@dashboard_blueprint.route('/trainings/<int:training_id>/delete', methods=['POST'])
@login_required
def delete_training(training_id):
    training = Training.query.get_or_404(training_id)

    # Invalidate the cached trainings and gallery images
    redisClient.delete('all_trainings')
    redisClient.delete('latest_trainings')
    # Now delete the training itself
    db.session.delete(training)
    db.session.commit()

    flash('training and its images deleted successfully!', 'training_creation_success')
    return redirect(url_for('dashboard.dash_training_catalog'))