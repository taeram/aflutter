from flask.ext.wtf import Form
from wtforms.fields import TextField,\
						   PasswordField,\
						   BooleanField,\
						   DateField,\
						   SelectField
from wtforms.validators import Required
from datetime import datetime


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember = BooleanField('Remember Me', default=False)


class UserForm(Form):
    name = TextField('Name', validators=[Required()])
    role = SelectField('Role', choices=[('admin', 'admin'), ('user', 'user')], default='user', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
