from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class HomePageForm(FlaskForm):
    submitHome = SubmitField('Home')
    
class LogoutForm(FlaskForm):
    submitLogout = SubmitField('Logout')
    
class SignupForm(FlaskForm):
    first = StringField('First Name', validators=[DataRequired()])
    last = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create Account')

class PairForm(FlaskForm):
    deviceID = SelectField('Device ID', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9')], validators=[DataRequired()])
    deviceType = SelectField('Device Type', choices=[('MatterLight','Matter Light'),('MatterSwitch','Matter Switch')], validators=[DataRequired()])
    deviceName = StringField('Device Name', validators=[DataRequired()])
    deviceStatus = 0
    deviceLevel = 127
    submit = SubmitField('Pair Device')

class DeleteForm(FlaskForm):
    deleteFm = SubmitField('Delete Account')

class RemoveDeviceForm(FlaskForm):
    submit = SubmitField('Remove Device')
    