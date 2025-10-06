from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Optional, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])

class UserForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha',
                                   validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais')])
    name = StringField('Nome Completo', validators=[DataRequired(), Length(max=100)])
    role = SelectField('Função', choices=[('admin', 'Administrador'), ('teacher', 'Docente')], validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])

class UserEditForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=80)])
    name = StringField('Nome Completo', validators=[DataRequired(), Length(max=100)])
    role = SelectField('Função', choices=[('admin', 'Administrador'), ('teacher', 'Docente')], validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    is_active = SelectField('Status', choices=[('True', 'Ativo'), ('False', 'Inativo')], validators=[DataRequired()])

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Nova Senha',
                                   validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais')])
