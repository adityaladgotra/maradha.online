import os
import uuid
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user

from app import app, db
from models import Admin, Student, Course, Enrollment, Notification
from forms import AdminLoginForm, StudentLoginForm, StudentRegistrationForm, CourseForm, EnrollmentForm, AdminStudentUploadForm

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
        
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        
        if admin and admin.check_password(form.password.data):
            login_user(admin, remember=form.remember_me.data)
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
    if not isinstance(current_user, Admin):
        return redirect(url_for('home'))
        
    courses = Course.query.order_by(Course.created_at.desc()).all()
    enrollments = Enrollment.query.order_by(Enrollment.created_at.desc()).all()
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('admin_dashboard.html', courses=courses, enrollments=enrollments, students=students)

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
        
        # Create notifications for all students about the new course
        students = Student.query.all()
        for student in students:
            notification = Notification(
                title="New Course Available",
                message=f"A new course '{course.title}' is now available for enrollment.",
                student_id=student.id,
                course_id=course.id
            )
            db.session.add(notification)
        db.session.commit()
        
        flash('Course added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_course.html', form=form)

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
    
    return render_template('edit_course.html', form=form, course=course)

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
    return render_template('enrollment_detail.html', enrollment=enrollment)

# Student registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        student = Student(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            phone_number=form.phone_number.data,
        )
        student.set_password(form.password.data)
        db.session.add(student)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

# Student login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('student_dashboard'))
    
    form = StudentLoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(username=form.username.data).first()
        
        if student and student.check_password(form.password.data):
            login_user(student, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Logged in successfully!', 'success')
            return redirect(next_page or url_for('student_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)

# Student logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# Student dashboard
@app.route('/dashboard')
@login_required
def student_dashboard():
    if not isinstance(current_user, Student):
        return redirect(url_for('admin_dashboard'))
    
    enrolled_courses = [enrollment.course for enrollment in current_user.enrollments]
    notifications = Notification.query.filter_by(student_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    return render_template('student_dashboard.html', enrolled_courses=enrolled_courses, notifications=notifications)

# Mark notification as read
@app.route('/notification/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    if not isinstance(current_user, Student):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.student_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})

# Admin Add Student
@app.route('/admin/student/add', methods=['GET', 'POST'])
@login_required
def admin_add_student():
    if not isinstance(current_user, Admin):
        return redirect(url_for('home'))
        
    form = AdminStudentUploadForm()
    
    if form.validate_on_submit():
        # Create the student
        student = Student(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            phone_number=form.phone_number.data
        )
        student.set_password(form.password.data)
        db.session.add(student)
        db.session.flush()  # Get the student ID before committing
        
        # Save the student photo if provided
        if form.student_photo.data:
            filename = secure_filename(f"student_{student.id}_{int(datetime.now().timestamp())}.jpg")
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.student_photo.data.save(photo_path)
            
            # Create an enrollment for this student
            enrollment = Enrollment(
                full_name=form.full_name.data,
                father_name="Added by Admin",  # Placeholder
                mother_name="Added by Admin",  # Placeholder
                phone_number=form.phone_number.data,
                whatsapp_number=form.phone_number.data,  # Using same number as placeholder
                email=form.email.data,
                address="Added via Admin Panel",  # Placeholder
                village_town="Added via Admin",  # Placeholder
                district="Added via Admin",  # Placeholder
                state="Added via Admin",  # Placeholder
                pin_code="000000",  # Placeholder
                education_status="Added via Admin Panel",  # Placeholder
                why_learn="Added via Admin Panel",  # Placeholder
                id_photo_path=os.path.join('uploads', filename),
                course_id=form.course_id.data,
                student_id=student.id
            )
            db.session.add(enrollment)
        else:
            # Create an enrollment without photo
            enrollment = Enrollment(
                full_name=form.full_name.data,
                father_name="Added by Admin",  # Placeholder
                mother_name="Added by Admin",  # Placeholder
                phone_number=form.phone_number.data,
                whatsapp_number=form.phone_number.data,  # Using same number as placeholder
                email=form.email.data,
                address="Added via Admin Panel",  # Placeholder
                village_town="Added via Admin",  # Placeholder
                district="Added via Admin",  # Placeholder
                state="Added via Admin",  # Placeholder
                pin_code="000000",  # Placeholder
                education_status="Added via Admin Panel",  # Placeholder
                why_learn="Added via Admin Panel",  # Placeholder
                course_id=form.course_id.data,
                student_id=student.id
            )
            db.session.add(enrollment)
            
        db.session.commit()
        
        # Add notification for the student
        course = Course.query.get(form.course_id.data)
        notification = Notification(
            title="Welcome to Maradha Institute",
            message=f"You have been enrolled in the course '{course.title}' by the admin.",
            student_id=student.id,
            course_id=course.id
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Student added and enrolled in the course successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin_add_student.html', form=form)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
