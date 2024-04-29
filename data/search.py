import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlite3
from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms.fields import StringField, TextAreaField
from wtforms.fields import BooleanField, SubmitField
from wtforms.validators import DataRequired
import os
import uuid as uuid
from werkzeug.utils import secure_filename


class SearchForm(FlaskForm):
    searched = StringField('Пойск', validators=[DataRequired()])
    submit = SubmitField('Применить')
