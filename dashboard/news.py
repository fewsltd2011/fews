from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import dashboard_blueprint
from models import News, db
from redis_client import redisClient
import cloudinary.uploader
import datetime


@dashboard_blueprint.route('/news', methods=['GET'])
@login_required
def dash_news():
    # Check if news are cached in Redis
    cached_news = redisClient.get('all_news')

    if cached_news:
        news = eval(cached_news)  # Convert string to list of dictionaries
    else:
        news = News.query.all()
        # Cache the result for 10 minutes (600 seconds)
        redisClient.setex('all_news', 600, str([new.to_dict() for new in news]))

    return render_template('dash_news.html', news=news)


@dashboard_blueprint.route('/news', methods=['POST'])
@login_required
def create_news():
    if request.method == 'POST':
        # Retrieve form data
        type = request.form.get('type')
        desc = request.form.get('desc')
        title = request.form.get('title')
        file = request.files.get('file')
        content = request.form.get('content')

        # Validate form data
        if not (title and desc and file and content and type):
            flash('All fields are required.', 'news_creation_error')
            return redirect(url_for('dashboard.dash_news'))
        
        if not file:
            flash('Image file is required.', 'news_creation_error')
            return redirect(url_for('dashboard.dash_news'))

        try:
            # Upload the file to Cloudinary
            upload_result = cloudinary.uploader.upload(file)

            # Get the URL of the uploaded image
            image_url = upload_result.get('url')
        except Exception as e:
            flash(f"Image upload failed: {str(e)}", 'news_creation_error')
            return redirect(url_for('dashboard.dash_news'))


        # Create a new new and add it to the database
        new_new = News(
            title=title,  # Use the uploaded image URL
            desc=desc,
            content=content,
            type=type,
            image_url=image_url
        )
        db.session.add(new_new)
        db.session.commit()

        # Invalidate the cached news
        redisClient.delete('all_news')
        redisClient.delete('latest_news')
        redisClient.delete('company_news')
        redisClient.delete('industry_news')

        flash('News created successfully!', 'news_creation_success')
        return redirect(url_for('dashboard.dash_news'))


@dashboard_blueprint.route('/news/<int:news_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_news(news_id):
    new = News.query.get_or_404(news_id)

    if request.method == 'POST':
        new.title = request.form['title']
        new.desc = request.form['desc']
        new.content = request.form['content']
        new.type = request.form['type']
        
        
        file = request.files.get('file')
        if file:
            # If there's an existing image, delete it from Cloudinary
            if new.image_url:
                public_id = new.image_url.split('/')[-1].split('.')[0]  # Extract public ID from the image URL
                try:
                    cloudinary.uploader.destroy(public_id)  # Delete existing image from Cloudinary
                except Exception as e:
                    flash(f"Failed to delete the existing image: {str(e)}", 'news_creation_error')
                    return redirect(url_for('dashboard.dash_news'))

            # Upload the new image to Cloudinary
            try:
                upload_result = cloudinary.uploader.upload(file)
                image_url = upload_result.get('url')  # Get the URL of the uploaded image
                new.image_url = image_url  # Update the image URL in the database
            except Exception as e:
                flash(f"Image upload failed: {str(e)}", 'news_creation_error')
                return redirect(url_for('dashboard.dash_news'))
        
        
        # Commit the changes to the database
        db.session.commit()

        # Invalidate the cached news
        redisClient.delete('all_news')
        redisClient.delete('latest_news')
        redisClient.delete('company_news')
        redisClient.delete('industry_news')

        flash('News updated successfully!', 'news_creation_success')
        return redirect(url_for('dashboard.dash_news'))

    return render_template('dash_edit_news.html', news=new)


@dashboard_blueprint.route('/news/<int:news_id>', methods=['GET'])
@login_required
def preview_news(news_id):
    
    new = News.query.get_or_404(news_id)

    return render_template('dash_news_preview.html', news=new)


@dashboard_blueprint.route('/news/<int:news_id>/delete', methods=['POST'])
@login_required
def delete_news(news_id):
    new = News.query.get_or_404(news_id)

    # Invalidate the cached news and gallery images
    redisClient.delete('all_news')
    redisClient.delete('latest_news')
    redisClient.delete('company_news')
    redisClient.delete('industry_news')
    
    if new.image_url:
        public_id = new.image_url.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(public_id)
    # Now delete the new itself
    db.session.delete(new)
    db.session.commit()

    flash('News deleted successfully!', 'news_creation_success')
    return redirect(url_for('dashboard.dash_news'))