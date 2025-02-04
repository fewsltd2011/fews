from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required  # Import the login_required decorator
from . import dashboard_blueprint  # Import the blueprint
from models import ContactUs, Hero, News, Project, Training, db
from redis_client import redisClient
import cloudinary.uploader

@dashboard_blueprint.route('/', methods=['GET'])
@login_required
def dash_main():
    
    cached_slides = redisClient.get('all_slides')
    record_counts = {
        'news_count': News.query.count(),
        'projects_count': Project.query.count(),
        'trainings_count': Training.query.count(),
        'contact_us_count': ContactUs.query.count(),
    }

    if cached_slides:
        slides = eval(cached_slides)  # Convert string to list of dictionaries
    else:
        slides = Hero.query.all()
        # Cache the result for 10 minutes (600 seconds)
        redisClient.setex('all_slides', 600, str([slide.to_dict() for slide in slides]))
        
    return render_template('dash_index.html', slides=slides, record_counts=record_counts)



@dashboard_blueprint.route('/slides', methods=['POST'])
@login_required
def create_slide():
    if request.method == 'POST':
        # Retrieve form data
        title = request.form.get('title')
        desc = request.form.get('desc')
        file = request.files.get('image_url')

        # Validate form data
        if not (title and desc):
            flash('All fields are required.', 'slide_creation_error')
            return redirect(url_for('dashboard.dash_main'))

        # Check if a file was uploaded
        if not file:
            flash('Image file is required.', 'slide_creation_error')
            return redirect(url_for('dashboard.dash_main'))

        try:
            # Upload the file to Cloudinary
            upload_result = cloudinary.uploader.upload(file)

            # Get the URL of the uploaded image
            image_url = upload_result.get('url')
        except Exception as e:
            flash(f"Image upload failed: {str(e)}", 'slide_creation_error')
            return redirect(url_for('dashboard.dash_main'))

        new_slide = Hero(
            title=title,
            image_url=image_url,  # Use the uploaded image URL
            desc=desc
        )
        db.session.add(new_slide)
        db.session.commit()

        redisClient.delete('all_slides')

        flash('slide created successfully!', 'slide_creation_success')
        return redirect(url_for('dashboard.dash_main'))


@dashboard_blueprint.route('/slides/<int:slide_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_slide(slide_id):
    slide = Hero.query.get_or_404(slide_id)

    if request.method == 'POST':
        slide.title = request.form['title']
        slide.desc = request.form['desc']

        # Handle image upload if a new file is provided
        file = request.files.get('image_url')
        if file:
            # If there's an existing image, delete it from Cloudinary
            if slide.image_url:
                public_id = slide.image_url.split('/')[-1].split('.')[0]  # Extract public ID from the image URL
                try:
                    cloudinary.uploader.destroy(public_id)  # Delete existing image from Cloudinary
                except Exception as e:
                    flash(f"Failed to delete the existing image: {str(e)}", 'slide_creation_error')
                    return redirect(url_for('dashboard.dash_main'))

            # Upload the new image to Cloudinary
            try:
                upload_result = cloudinary.uploader.upload(file)
                image_url = upload_result.get('url')  # Get the URL of the uploaded image
                slide.image_url = image_url  # Update the image URL in the database
            except Exception as e:
                flash(f"Image upload failed: {str(e)}", 'slide_creation_error')
                return redirect(url_for('dashboard.dash_main'))

        # Commit the changes to the database
        db.session.commit()

        redisClient.delete('all_slides')

        flash('slide updated successfully!', 'slide_creation_success')
        return redirect(url_for('dashboard.dash_main'))

    return render_template('dash_edit_slide.html', slide=slide)

@dashboard_blueprint.route('/slides/<int:slide_id>/delete', methods=['POST'])
@login_required
def delete_slide(slide_id):
    slide = Hero.query.get_or_404(slide_id)
    
    redisClient.delete('all_slides')

    # Delete the main image from Cloudinary (if it exists)
    if slide.image_url:
        public_id = slide.image_url.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(public_id)

    db.session.delete(slide)
    db.session.commit()

    flash('Slide deleted successfully!', 'slide_creation_success')
    return redirect(url_for('dashboard.dash_main'))

