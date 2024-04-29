import flask

from data import db_session
from data.news import News

blueprint = flask.Blueprint('news_api', __name__, template_folder='templates')


@blueprint.route('/api/news')
def api_news():
    "return 'Обработчик в news_api'"
    db_sess = db_session.create_session()
    news = db_session.query(News).all()
    return flask.jsonify({'news': [item.to_dict(only=('title', 'content', 'user_id')) for item in news]})

    # в папке
