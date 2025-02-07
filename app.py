from datetime import datetime
import os
import re
from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from flask.cli import with_appcontext
from flask_migrate import Migrate
from config import Config
from create_admin import create_admin_account
from dashboard import dashboard_blueprint
from models import ContactUs, Hero, News, Project, ProjectGallery, Training, TrainingRequest, UpcomingTraining, User, db
from flask_login import LoginManager
import cloudinary
from redis_client import redisClient
from specific_tailwind import style_html_with_tailwind

app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = 'dashboard.login'
# Initialize extensions
redisClient.init_app(app)

db.init_app(app)
migrate = Migrate(app, db)

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def parse_date(date_string, format='%Y-%m-%d'):
    if not date_string or not isinstance(date_string, str):
        return ''  # Return an empty string or a default value
    try:
        return datetime.fromisoformat(date_string).strftime(format)
    except ValueError:
        return ''
    
def parse_date_year(datetime_string):
    print(type(datetime_string), datetime_string)

    try:
        if isinstance(datetime_string, str):
            parsed_datetime = datetime.fromisoformat(datetime_string)
        else:
            parsed_datetime = datetime_string
        return parsed_datetime.strftime('%b %d, %Y')
    except ValueError:
        return ''

app.jinja_env.filters['parse_date'] = parse_date

app.jinja_env.filters['parse_date_year'] = parse_date_year


app.jinja_env.filters['style_with_tailwind'] = style_html_with_tailwind

app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')

@app.route('/')
def home():
    cached_slides = redisClient.get('all_slides')
    cached_trainings = redisClient.get('latest_trainings')
    cached_news = redisClient.get('latest_news')

    if cached_slides:
        slides = eval(cached_slides)
    else:
        slides = Hero.query.all()
        redisClient.setex('all_slides', 600, str([slide.to_dict() for slide in slides]))
        
    if cached_trainings:
        trainings = eval(cached_trainings)
    else:
        trainings = (
                    Training.query.order_by(Training.created_at.desc())
                    .limit(2)
                    .all()
                )
        redisClient.setex('latest_trainings', 600, str([training.to_dict() for training in trainings]))
        
    if cached_news:
        news = eval(cached_news)
    else:
        news = (
                    News.query.order_by(News.created_at.desc())
                    .limit(3)
                    .all()
                )
        redisClient.setex('cached_news', 600, str([new.to_dict() for new in news]))
        
        
    return render_template('index.html', slides=slides, trainings=trainings, news=news)

@app.route('/about-us')
def about_us():
    return render_template('who-we-are/about-us.html')

@app.route('/company-profile')
def company_profile():
    return render_template('who-we-are/company-profile.html')


@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/projects')
def projects():
    
    cached_projects = redisClient.get('all_projects')
    
    if cached_projects:
        projects = eval(cached_projects)
    else:
        projects = Project.query.all()
        redisClient.setex('all_projects', 600, str([project.to_dict() for project in projects]))
        
    return render_template('projects.html', projects=projects)

@app.route('/project/<int:project_id>')
def project(project_id):
    
    project = Project.query.get(project_id)
    gallery_images = ProjectGallery.query.filter_by(project_id=project_id).all()
    
    return render_template('project.html', project=project, gallery_images=gallery_images)

@app.route('/company-news')
def company_news():
    
    cached_news = redisClient.get('company_news')
    
    if cached_news:
        news = eval(cached_news)
    else:
        news = News.query.filter_by(type='company').order_by(News.created_at.desc()).all()
        redisClient.setex('company_news', 600, str([new.to_dict() for new in news]))
        
    return render_template('news/company.html', news=news)

@app.route('/industry-news')
def industry_news():
    
    cached_news = redisClient.get('industry_news')
    
    if cached_news:
        news = eval(cached_news)
    else:
        news = News.query.filter_by(type='industry').order_by(News.created_at.desc()).all()
        redisClient.setex('industry_news', 600, str([new.to_dict() for new in news]))
        
    return render_template('news/industry.html', news=news)

@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    # Query the database for the blog by ID
    blog_post = News.query.get(blog_id)

    # Render the blog page with the retrieved blog details
    return render_template('blog.html', blog=blog_post)

@app.route('/training-catalog')
def training_catalog():
    
    cached_trainings = redisClient.get('all_trainings')

    if cached_trainings:
        trainings = eval(cached_trainings)  # Convert string to list of dictionaries
    else:
        trainings = Training.query.all()
        # Cache the result for 10 minutes (600 seconds)
        redisClient.setex('all_trainings', 600, str([training.to_dict() for training in trainings]))
        
    return render_template("training-hub/training-catalog.html", trainings=trainings)

@app.route('/upcoming-training')
def upcoming_training():
    
    cached_trainings = redisClient.get('all_upcoming_trainings_site')

    if cached_trainings:
        trainings = eval(cached_trainings)  # Convert string to list of dictionaries
    else:
        trainings = UpcomingTraining.query.filter_by(status='active').all()
        # Cache the result for 10 minutes (600 seconds)
        redisClient.setex('all_upcoming_trainings_site', 600, str([training.to_dict() for training in trainings]))

    return render_template("training-hub/upcoming-training.html", trainings=trainings)

@app.route('/training/<int:training_id>')
def detailed_training(training_id):
    
    training = Training.query.get(training_id)

    return render_template("training-hub/detailed-training.html", training=training)

@app.route('/training-request/<int:training_id>', methods=['GET', 'POST'])
def training_request(training_id):
    upcomingTraining = UpcomingTraining.query.filter_by(id=training_id, status='active').first()

    if not upcomingTraining:
        return render_template("training-hub/training-request.html", training=None, upcomingTraining=upcomingTraining)

    if request.method == 'POST':
        try:
            # Form fields
            name = request.form.get('name')
            gender = request.form.get('gender')
            organization = request.form.get('organization')
            organization_address = request.form.get('organization_address')
            job_title = request.form.get('job_title')
            email = request.form.get('email')
            street_address = request.form.get('street_address')
            city = request.form.get('city')
            telephone = request.form.get('telephone')

            # Validation rules
            errors = []

            if not name or not re.match(r'^[a-zA-Z\s]+$', name):
                errors.append("Invalid name. Only letters and spaces are allowed.")

            if gender not in ['Male', 'Female']:
                errors.append("Invalid gender selection.")

            if not organization:
                errors.append("Organization is required.")

            if not organization_address:
                errors.append("Organization address is required.")

            if not job_title:
                errors.append("Job title is required.")

            if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                errors.append("Invalid email address.")

            if not street_address:
                errors.append("Street address is required.")

            if not city or not re.match(r'^[a-zA-Z\s]+$', city):
                errors.append("Invalid city name. Only letters and spaces are allowed.")

            if not telephone or not re.match(r'^\+?[0-9]{7,15}$', telephone):
                errors.append("Invalid telephone number. Use a valid format.")

            # If there are errors, display them
            if errors:
                for error in errors:
                    flash(error, 'req_creation_error')
                return render_template("training-hub/training-request.html", training=upcomingTraining.training, upcomingTraining=upcomingTraining)

            # If validation passes, save the request
            new_request = TrainingRequest(
                name=name,
                gender=gender,
                organization=organization,
                organization_address=organization_address,
                job_title=job_title,
                email=email,
                street_address=street_address,
                city=city,
                telephone=telephone,
                upcoming_training_id=training_id
            )
            db.session.add(new_request)
            db.session.commit()

            # Clear Redis cache
            redisClient.delete('all_upcoming_trainings')

            flash("Training request submitted successfully!", "req_creation_success")
            return redirect(url_for('training_request', training_id=training_id))

        except Exception as e:
            # Log the error for debugging purposes
            app.logger.error(f"An error occurred: {str(e)}")

            # Flash a generic error message to the user
            flash("An unexpected error occurred while processing your request. Please try again.", "req_creation_error")
            return render_template("training-hub/training-request.html", training=upcomingTraining.training, upcomingTraining=upcomingTraining)

    return render_template("training-hub/training-request.html", training=upcomingTraining.training, upcomingTraining=upcomingTraining)

@app.route('/upcoming-training/<int:training_id>')
def detailed_upcoming_training(training_id):
    
    upcomingTraining = UpcomingTraining.query.filter_by(id=training_id, status='active').first()

    if not upcomingTraining:
        return render_template("training-hub/detailed-upcoming_training.html", training=None, upcomingTraining=upcomingTraining)

    return render_template("training-hub/detailed-upcoming_training.html", training=upcomingTraining.training, upcomingTraining=upcomingTraining)

@app.route('/contact-us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        try:
            # Retrieve form data
            name = request.form.get('name')
            email = request.form.get('email')
            phonenumber = request.form.get('phonenumber')
            message = request.form.get('message')

            # Validate all required fields
            if not name or not email or not phonenumber or not message:
                flash("All fields are required!", "feedback_creation_error")
                return redirect(url_for('contact_us'))

            # Validate phone number (example: must be 10 digits)
            phone_regex = re.compile(r'^\d{10}$')
            if not phone_regex.match(phonenumber):
                flash("Invalid phone number! Please enter a 10-digit phone number.", "error")
                return redirect(url_for('contact_us'))

            # Save the data to the database
            new_project = ContactUs(
                name=name,
                email=email,
                phone_number=phonenumber,
                message=message
            )
            db.session.add(new_project)
            db.session.commit()

            # Clear cache for all feedbacks
            redisClient.delete('all_feedbacks')

            # If everything succeeds
            flash("Form submitted successfully!", "feedback_creation_success")
            return redirect(url_for('contact_us'))

        except Exception as e:
            # Log the error for debugging
            app.logger.error(f"An error occurred: {str(e)}")

            # Inform the user about the error
            flash("An unexpected error occurred while processing your request. Please try again.", "feedback_creation_error")
            return redirect(url_for('contact_us'))

    return render_template("contact-us.html")

@app.route('/robots.txt')
def serve_robots():
    return send_from_directory('static', 'robots.txt')


@app.route('/sitemap.xml')
def serve_sitemap():
    return send_from_directory('static', 'sitemap.xml')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.cli.command('create-admin')
@with_appcontext
def create_admin():
    """Creates the admin user."""
    create_admin_account()

if __name__ == '__main__':
    app.run(debug=True)
