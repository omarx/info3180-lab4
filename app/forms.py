from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class UploadForm(FlaskForm):
    file = FileField('Image', validators=[
        FileRequired(message='File is required.'),
        FileAllowed(['jpg', 'png'], message='Only image files (jpg, png) are allowed.')
    ])
    submit = SubmitField('Upload')