import cloudinary.uploader
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import dashboard_blueprint
from models import Project, ProjectGallery, db
from redis_client import redisClient


@dashboard_blueprint.route('/projects', methods=['GET'])
@login_required
def dash_projects():
    # Check if projects are cached in Redis
    cached_projects = redisClient.get('all_projects')

    if cached_projects:
        projects = eval(cached_projects)  # Convert string to list of dictionaries
    else:
        projects = Project.query.all()
        # Cache the result for 10 minutes (600 seconds)
        redisClient.setex('all_projects', 600, str([project.to_dict() for project in projects]))

    return render_template('dash_projects.html', projects=projects)


@dashboard_blueprint.route('/projects', methods=['POST'])
@login_required
def create_project():
    if request.method == 'POST':
        # Retrieve form data
        title = request.form.get('title')
        desc = request.form.get('desc')
        status = request.form.get('status')
        period = request.form.get('period')
        scope_of_service = request.form.get('scope_of_service')
        project_location = request.form.get('project_location')
        funder = request.form.get('funder')
        client = request.form.get('client')
        file = request.files.get('image_url')  # Retrieve the uploaded file

        # Validate form data
        if not (title and desc and status and period and scope_of_service and project_location and funder and client):
            flash('All fields are required.', 'project_creation_error')
            return redirect(url_for('dashboard.dash_projects'))

        # Check if a file was uploaded
        if not file:
            flash('Image file is required.', 'project_creation_error')
            return redirect(url_for('dashboard.dash_projects'))

        try:
            # Upload the file to Cloudinary
            upload_result = cloudinary.uploader.upload(file)

            # Get the URL of the uploaded image
            image_url = upload_result.get('url')
        except Exception as e:
            flash(f"Image upload failed: {str(e)}", 'project_creation_error')
            return redirect(url_for('dashboard.dash_projects'))

        # Create a new project and add it to the database
        new_project = Project(
            title=title,
            image_url=image_url,  # Use the uploaded image URL
            desc=desc,
            status=status,
            period=period,
            scope_of_service=scope_of_service,
            project_location=project_location,
            funder=funder,
            client=client
        )
        db.session.add(new_project)
        db.session.commit()

        # Invalidate the cached projects
        redisClient.delete('all_projects')

        flash('Project created successfully!', 'project_creation_success')
        return redirect(url_for('dashboard.dash_projects'))


@dashboard_blueprint.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        project.title = request.form['title']
        project.desc = request.form['desc']
        project.status = request.form['status']
        project.period = request.form['period']
        project.scope_of_service = request.form['scope_of_service']
        project.project_location = request.form['project_location']
        project.funder = request.form['funder']
        project.client = request.form['client']

        # Handle image upload if a new file is provided
        file = request.files.get('image_url')
        if file:
            # If there's an existing image, delete it from Cloudinary
            if project.image_url:
                public_id = project.image_url.split('/')[-1].split('.')[0]  # Extract public ID from the image URL
                try:
                    cloudinary.uploader.destroy(public_id)  # Delete existing image from Cloudinary
                except Exception as e:
                    flash(f"Failed to delete the existing image: {str(e)}", 'project_creation_error')
                    return redirect(url_for('dashboard.dash_projects'))

            # Upload the new image to Cloudinary
            try:
                upload_result = cloudinary.uploader.upload(file)
                image_url = upload_result.get('url')  # Get the URL of the uploaded image
                project.image_url = image_url  # Update the image URL in the database
            except Exception as e:
                flash(f"Image upload failed: {str(e)}", 'project_creation_error')
                return redirect(url_for('dashboard.dash_projects'))

        # Commit the changes to the database
        db.session.commit()

        # Invalidate the cached projects
        redisClient.delete('all_projects')

        flash('Project updated successfully!', 'project_creation_success')
        return redirect(url_for('dashboard.dash_projects'))

    return render_template('dash_edit_project.html', project=project)


@dashboard_blueprint.route('/projects/<int:project_id>', methods=['GET'])
@login_required
def preview_project(project_id):
    # Check if gallery images are cached in Redis
    cached_gallery_images = redisClient.get(f'project_{project_id}_gallery')
    project = Project.query.get_or_404(project_id)

    if cached_gallery_images:
        gallery_images = eval(cached_gallery_images)
    else:
        gallery_images = [gallery_image.to_dict() for gallery_image in project.gallery]
        # Cache the gallery images for 5 minutes
        redisClient.setex(f'project_{project_id}_gallery', 300, str(gallery_images))

    return render_template('dash_project_preview.html', project=project, gallery_images=gallery_images)


@dashboard_blueprint.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)

    # Invalidate the cached projects and gallery images
    redisClient.delete('all_projects')
    redisClient.delete(f'project_{project_id}_gallery')

    # Delete the main image from Cloudinary (if it exists)
    if project.image_url:
        public_id = project.image_url.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(public_id)

    # Delete all images in the project's gallery from Cloudinary
    for gallery_image in project.gallery:
        if gallery_image.image_url:
            public_id = gallery_image.image_url.split('/')[-1].split('.')[0]
            cloudinary.uploader.destroy(public_id)
            db.session.delete(gallery_image)

    # Now delete the project itself
    db.session.delete(project)
    db.session.commit()

    flash('Project and its images deleted successfully!', 'project_creation_success')
    return redirect(url_for('dashboard.dash_projects'))


@dashboard_blueprint.route('/delete-image/<int:image_id>', methods=['POST'])
@login_required
def delete_project_image(image_id):
    image = ProjectGallery.query.get_or_404(image_id)
    try:
        # Delete image from Cloudinary
        public_id = image.image_url.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(public_id)
        
        # Delete image from the database
        db.session.delete(image)
        db.session.commit()

        # Invalidate cache for project gallery
        redisClient.delete(f'project_{image.project_id}_gallery')

        flash('Image deleted successfully!', 'project_creation_success')
    except Exception as e:
        flash(f'Error deleting image: {str(e)}', 'project_creation_error')
    
    return redirect(url_for('dashboard.preview_project', project_id=image.project_id))


@dashboard_blueprint.route('/upload-gallery-image/<int:project_id>', methods=['POST'])
@login_required
def upload_gallery_image(project_id):
    project = Project.query.get_or_404(project_id)
    image_file = request.files.get('image')
    if image_file:
        upload_result = cloudinary.uploader.upload(image_file)
        image_url = upload_result.get('url')
        
        # Save image URL to the gallery
        new_image = ProjectGallery(project_id=project.id, image_url=image_url)
        db.session.add(new_image)
        db.session.commit()

        # Invalidate the gallery cache
        redisClient.delete(f'project_{project_id}_gallery')

        flash('Image added to gallery!', 'project_creation_success')
    
    return redirect(url_for('dashboard.preview_project', project_id=project.id))
