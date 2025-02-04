from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug.security import generate_password_hash
from . import dashboard_blueprint
from models import User, db


@dashboard_blueprint.route('/users', methods=['GET', 'POST'])
@login_required
def dash_users():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            flash('All fields are required.', 'user_creation_error')
            return redirect(url_for('dashboard.dash_users'))

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use. Please choose a different one.', 'user_creation_error')
            return redirect(url_for('dashboard.dash_users'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new user and add it to the database
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Flash success message and redirect
        flash('User created successfully!', 'user_creation_success')
        return redirect(url_for('dashboard.dash_users'))
    users = User.query.all()
    
    return render_template('dash_users.html', users=users)
