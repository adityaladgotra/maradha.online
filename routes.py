import os
import uuid
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user

from app import app, db
from models import Admin, Course, Enrollment
from forms import LoginForm, CourseForm, EnrollmentForm

# Home page
@app.route('/')
def home():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('home.html', courses=courses)

# Course detail page
@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    form = EnrollmentForm()
    return render_template('course_detail.html', course=course, form=form)

# Enrollment form submission
@app.route('/enroll/<int:course_id>', methods=['GET', 'POST'])
def enrollment_form(course_id):
    course = Course.query.get_or_404(course_id)
    form = EnrollmentForm()
    
    if form.validate_on_submit():
        # Handle file upload if provided
        id_photo_path = None
        if form.id_photo.data:
            filename = secure_filename(f"{uuid.uuid4()}_{form.id_photo.data.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.id_photo.data.save(filepath)
            id_photo_path = os.path.join('uploads', filename)
        
        # Create enrollment
        enrollment = Enrollment(
            full_name=form.full_name.data,
            father_name=form.father_name.data,
            mother_name=form.mother_name.data,
            phone_number=form.phone_number.data,
            whatsapp_number=form.whatsapp_number.data,
            email=form.email.data,
            address=form.address.data,
            village_town=form.village_town.data,
            district=form.district.data,
            state=form.state.data,
            pin_code=form.pin_code.data,
            education_status=form.education_status.data,
            why_learn=form.why_learn.data,
            id_photo_path=id_photo_path,
            course_id=course.id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        # Set success message in localStorage (handled by JS)
        flash('Application submitted successfully! We will contact you soon.', 'success')
        return redirect(url_for('home', enrollment_success=True))
    
    return render_template('enrollment_form.html', form=form, course=course)

# Admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        
        if admin and check_password_hash(admin.password_hash, form.password.data):
            login_user(admin)
            next_page = request.args.get('next')
            flash('Logged in successfully!', 'success')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('admin_login.html', form=form)

# Admin logout
@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# Admin dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    enrollments = Enrollment.query.order_by(Enrollment.created_at.desc()).all()
    return render_template('admin_dashboard.html', courses=courses, enrollments=enrollments)

# Add new course
@app.route('/admin/course/add', methods=['GET', 'POST'])
@login_required
def add_course():
    form = CourseForm()
    
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            price=form.price.data,
            offer_price=form.offer_price.data,
            image_url=form.image_url.data,
            benefits=form.benefits.data
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash('Course added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_dashboard.html', form=form, action='add_course')

# Edit course
@app.route('/admin/course/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    
    if form.validate_on_submit():
        form.populate_obj(course)
        db.session.commit()
        
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_dashboard.html', form=form, course=course, action='edit_course')

# Delete course
@app.route('/admin/course/delete/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    db.session.delete(course)
    db.session.commit()
    
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Filter enrollments by course (AJAX)
@app.route('/admin/enrollments/filter/<int:course_id>')
@login_required
def filter_enrollments(course_id):
    enrollments = Enrollment.query.filter_by(course_id=course_id).order_by(Enrollment.created_at.desc()).all()
    
    enrollment_data = []
    for enrollment in enrollments:
        enrollment_data.append({
            'id': enrollment.id,
            'name': enrollment.full_name,
            'phone': enrollment.phone_number,
            'education': enrollment.education_status,
            'location': f"{enrollment.village_town}, {enrollment.district}, {enrollment.state}",
            'date': enrollment.created_at.strftime('%d %b, %Y')
        })
    
    return jsonify(enrollment_data)

# View enrollment details
@app.route('/admin/enrollment/<int:enrollment_id>')
@login_required
def enrollment_detail(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    return render_template('admin_dashboard.html', enrollment=enrollment, action='view_enrollment')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
