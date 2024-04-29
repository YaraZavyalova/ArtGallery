from io import BytesIO

from flask import Flask, render_template, redirect, request, make_response, session, abort, send_file, \
    send_from_directory
from data import db_session
from data.search import SearchForm
from data.users import User
from data.art import Art, ArtForm, ArtEditForm
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, logout_user, current_user, login_remembered, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
import os
import uuid as uuid
from werkzeug.utils import secure_filename


def create_user(name, about, email):
    user = User()
    user.name = name
    user.about = about
    user.email = email
    return user


def create_art(title, content, is_private):
    art = Art()
    art.title = title
    art.content = content
    art.is_private = is_private
    return art


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSHIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSHIONS


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/cookie_test')
def cookie_test():
    visit_count = int(request.cookies.get('visit_count', 0))
    if visit_count:
        res = make_response(f'Вы посетили страницу {visit_count + 1} раз')
        res.set_cookie('visit_count', str(visit_count + 1),
                       max_age=0)
    else:
        res = make_response(f'Вы посетили страницу первый раз за последний год')
        res.set_cookie('visit_count', '1', max_age=0)
    return res


@app.route('/session_test')
def session_test():
    visit_count = session.get('visit_count', 0)
    session['visit_count'] = visit_count + 1
    return make_response(f'Вы посетили эту страницу {visit_count + 1} раз')


@app.route('/serve_image/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], f'{filename}.jpg')


@app.route('/')
@app.route('/index')
def index():
    art = Art()
    if current_user == art.artist_user:
        print('yes')
    db_session.global_init('db/art.db')
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        art = db_sess.query(Art).filter((Art.artist_user == current_user) | (Art.is_private == 0))
    else:
        art = db_sess.query(Art).filter(Art.is_private == 0)
    d = art
    return render_template('index.html', art=art, current_user=current_user, title='Дамашняя страница')


@app.route('/profile')
def profile():
    art = Art()
    if current_user == art.artist_user:
        print('yes')
    db_session.global_init('db/art.db')
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        art = db_sess.query(Art).filter(Art.artist_user == current_user)
    else:
        art = db_sess.query(Art).filter(Art.artist_user == current_user)
    return render_template('profile.html', art=art, current_user=current_user, title='Профиль')


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    db_session.global_init('db/art.db')
    db_sess = db_session.create_session()
    search_data = form.searched.data
    if current_user.is_authenticated:
        form = db_sess.query(Art).filter(
            Art.title.icontains(search_data) | Art.description.icontains(search_data) |
            (Art.artist == search_data), ((Art.user == current_user) | (Art.is_private == 0)))
    else:
        form = db_sess.query(Art).filter(
            Art.title.icontains(search_data) | Art.description.icontains(search_data) |
            (Art.artist == search_data), (Art.is_private == 0))
    return render_template('search.html', searched=form, form=form, art=form, current_user=current_user,
                           title='Дамашняя страница')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        user = User(
            name=form.name.data,
            email=form.email.data,
            about_me=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/art', methods=['GET', 'POST'])
@login_required
def add_art():
    form = ArtForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        art = Art()
        art.title = form.title.data
        art.content = form.content.data
        art.description = form.description.data
        file_name = secure_filename(form.content.data.name)
        img_name = str(uuid.uuid1()) + "_" + file_name
        saver = form.content.data
        art.content = img_name
        art.is_private = form.is_private.data
        current_user.artist_user.append(art)
        db_sess.merge(current_user)
        db_sess.commit()
        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{img_name}.jpg"))
        return redirect('/')
    return render_template('art.html', title='Добавление новости', form=form)


@app.route('/art/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_art(id):
    form = ArtEditForm()
    db_sess = db_session.create_session()
    art = db_sess.query(Art).filter(Art.id == id,
                                    Art.artist == current_user.id
                                    ).first()
    if request.method == "GET":
        db_sess = db_session.create_session()
        art = db_sess.query(Art).filter(Art.id == id,
                                        Art.artist == current_user.id
                                        ).first()
        if art:
            form.title.data = art.title
            art.content = art.content
            form.description.data = art.description
            form.is_private.data = art.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        art = db_sess.query(Art).filter(Art.id == id,
                                        Art.artist == current_user.id
                                        ).first()
        if art:
            art.title = form.title.data
            art.content = art.content
            art.description = form.description.data
            art.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('art_edit.html',
                           title='Редактирование названия и описания',
                           form=form,
                           art=art
                           )


@app.route('/art_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def art_delete(id):
    db_sess = db_session.create_session()
    art = db_sess.query(Art).filter(Art.id == id,
                                    Art.artist == current_user.id
                                    ).first()
    if art:
        db_sess.delete(art)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init('db/art.db')
    db_sess = db_session.create_session()
    app.run()


if __name__ == '__main__':
    main()
