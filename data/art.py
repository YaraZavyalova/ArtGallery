import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms.fields import StringField, TextAreaField
from wtforms.fields import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ArtForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = FileField('Изображение', validators=[DataRequired()])
    description = TextAreaField('Информация об изображение', validators=[DataRequired()])
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')


class ArtEditForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    description = TextAreaField('Информация о изабражение', validators=[DataRequired()])
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')


class Art(SqlAlchemyBase):
    __tablename__ = 'art'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    artist = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    post_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                  default=datetime.datetime.now)
    art = FileField('Информация о изабражение', validators=[DataRequired()])
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    artist_user = sqlalchemy.orm.relationship('User')
