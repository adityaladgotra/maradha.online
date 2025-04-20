from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, DateField, FloatField, SelectField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError, EqualTo
import re
from models import Student, Course

class AdminLoginForm(FlaskForm):
    username = StringField('Admin Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login as Admin')

class StudentLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class StudentRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        student = Student.query.filter_by(username=username.data).first()
        if student:
            raise ValidationError('That username is already taken. Please choose a different one.')
            
    def validate_email(self, email):
        student = Student.query.filter_by(email=email.data).first()
        if student:
            raise ValidationError('That email is already registered. Please use a different one or login.')
            
    def validate_phone_number(self, field):
        if not re.match(r'^\d{10,15}$', field.data):
            raise ValidationError('Phone number must be 10-15 digits')

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Course Description', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    price = FloatField('Regular Price (₹)', validators=[DataRequired()])
    offer_price = FloatField('Offer Price (₹)', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=256)])
    benefits = TextAreaField('Benefits (Separate with new lines)', validators=[Optional()])
    submit = SubmitField('Save Course')
    
    def validate_end_date(self, field):
        if field.data < self.start_date.data:
            raise ValidationError('End date must be after start date')

class EnrollmentForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    father_name = StringField('Father\'s Name', validators=[DataRequired(), Length(max=100)])
    mother_name = StringField('Mother\'s Name', validators=[DataRequired(), Length(max=100)])
    
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    whatsapp_number = StringField('WhatsApp Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email ID (Optional)', validators=[Optional(), Email(), Length(max=120)])
    
    address = TextAreaField('Full Address', validators=[DataRequired()])
    village_town = StringField('Village/Town', validators=[DataRequired(), Length(max=100)])
    district = StringField('District', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[DataRequired(), Length(max=100)])
    pin_code = StringField('Pin Code', validators=[DataRequired(), Length(min=6, max=10)])
    
    education_status = StringField('Current Class / Pass-out Status', validators=[DataRequired(), Length(max=100)])
    why_learn = TextAreaField('Why You Want to Learn', validators=[DataRequired()])
    
    id_photo = FileField('Upload Student ID or Photo (Optional)', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Only images (jpg, jpeg, png) and PDF files are allowed!')
    ])
    
    submit = SubmitField('Submit Application')
    
    def validate_phone_number(self, field):
        if not re.match(r'^\d{10,15}$', field.data):
            raise ValidationError('Phone number must be 10-15 digits')
    
    def validate_whatsapp_number(self, field):
        if not re.match(r'^\d{10,15}$', field.data):
            raise ValidationError('WhatsApp number must be 10-15 digits')
    
    def validate_pin_code(self, field):
        if not re.match(r'^\d{6,10}$', field.data):
            raise ValidationError('Pin code must be 6-10 digits')

class AdminStudentUploadForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    student_photo = FileField('Student Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only images (jpg, jpeg, png) are allowed!')
    ])
    submit = SubmitField('Add Student')
    
    def __init__(self, *args, **kwargs):
        super(AdminStudentUploadForm, self).__init__(*args, **kwargs)
        # Populate the courses dropdown dynamically
        self.course_id.choices = [(course.id, course.title) 
                                  for course in Course.query.order_by(Course.title).all()]
    
    def validate_username(self, username):
        student = Student.query.filter_by(username=username.data).first()
        if student:
            raise ValidationError('That username is already taken. Please choose a different one.')
            
    def validate_email(self, email):
        student = Student.query.filter_by(email=email.data).first()
        if student:
            raise ValidationError('That email is already registered. Please use a different one.')
            
    def validate_phone_number(self, field):
        if not re.match(r'^\d{10,15}$', field.data):
            raise ValidationError('Phone number must be 10-15 digits')
