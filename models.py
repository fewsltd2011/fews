from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_active=db.Column(db.Boolean, default=True)

# News Model
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'desc': self.desc,
            'image_url': self.image_url,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    news = db.relationship('News', backref=db.backref('comments', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'news_id': self.news_id,
            'content': self.content,
            'username': self.username,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Project Model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    desc = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(200), nullable=False)
    period = db.Column(db.String(100), nullable=False)
    scope_of_service = db.Column(db.String(500), nullable=False)
    project_location = db.Column(db.String(500), nullable=False)
    funder = db.Column(db.String(300), nullable=False)
    client = db.Column(db.String(300), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'desc': self.desc,
            'image_url': self.image_url,
            'status': self.status,
            'project_location': self.project_location,
            'funder': self.funder,
            'client': self.client,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Project Gallery Model
class ProjectGallery(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    project = db.relationship('Project', backref=db.backref('gallery', lazy=True))
    
    def to_dict(self):
        return {'image_url': self.image_url}

# Training Model
class Training(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    number_of_cpds = db.Column(db.String(200), nullable=False, default=0)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    daily_schedule = db.Column(db.String(500), nullable=False)
    training_style = db.Column(db.String(500), nullable=False)
    online_knowledge_test = db.Column(db.String(500), default=False)
    certification = db.Column(db.String(500), default=False)
    instructor = db.Column(db.String(500), nullable=False)
    fees = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'desc': self.desc,
            'number_of_cpds': self.number_of_cpds,
            'content': self.content,
            'type': self.type,
            'duration': self.duration,
            'daily_schedule': self.daily_schedule,
            'training_style': self.training_style,
            'online_knowledge_test': self.online_knowledge_test,
            'certification': self.certification,
            'instructor': self.instructor,
            'fees': self.fees,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

# Upcoming Training Model
class UpcomingTraining(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    training_id = db.Column(db.Integer, db.ForeignKey('training.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)
    training = db.relationship('Training', backref=db.backref('upcoming_trainings', lazy=True))
    
    # Relationship to TrainingRequest
    training_requests = db.relationship('TrainingRequest', backref='upcoming_training', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'training_id': self.training_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status,
            'training': self.training.to_dict() if self.training else None,
            'training_requests': [training_request.to_dict() for training_request in self.training_requests] if self.training_requests else []
        }

class TrainingRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    organization = db.Column(db.String(200), nullable=False)
    organization_address = db.Column(db.String(500), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    street_address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key linking to UpcomingTraining
    upcoming_training_id = db.Column(db.Integer, db.ForeignKey('upcoming_training.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'organization': self.organization,
            'organization_address': self.organization_address,
            'job_title': self.job_title,
            'email': self.email,
            'street_address': self.street_address,
            'city': self.city,
            'telephone': self.telephone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<TrainingRequest {self.name}>'
# Contact Us Model
class ContactUs(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'message': self.message,
        }

# Hero Model
class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_url = db.Column(db.String(500))
    title = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        
        return {
            'id': self.id,
            'title': self.title,
            'desc': self.desc,
            'image_url': self.image_url
        }

# Notification Model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
