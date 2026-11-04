from flask import jsonify, request

from .error_handlers import InvalidAPIUsage
from .models import Opinion
from .views import random_opinion
from . import app, db


@app.route('/api/opinions/<int:id>/', methods=['GET'])
def get_opinion(id):
    opinion = db.session.get(Opinion, id)
    if opinion is None:
        raise InvalidAPIUsage(
            'Такого мнения нет в базе.',
            404
        )
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['PATCH'])
def update_opinion(id):
    opinion = db.session.get(Opinion, id)
    if opinion is None:
        raise InvalidAPIUsage(
            'Такого мнения нет в базе.',
            404
        )
    data = request.get_json()
    stmt = db.select(Opinion).where(Opinion.text == data['text'])
    if 'text' in data and db.session.scalar(stmt):
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    opinion.title = data.get('title', opinion.title)
    opinion.text = data.get('text', opinion.text)
    opinion.source = data.get('source', opinion.source)
    opinion.added_by = data.get('added_by', opinion.added_by)
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['DELETE'])
def delete_opinion(id):
    opinion = db.session.get(Opinion, id)
    if opinion is None:
        raise InvalidAPIUsage(
            'Такого мнения нет в базе.',
            404
        )
    db.session.delete(opinion)
    db.session.commit()
    return '', 204


@app.route('/api/opinions/', methods=['GET'])
def get_opinions():
    opinions = Opinion.query.all()
    opinions_list = [opinion.to_dict() for opinion in opinions]
    return jsonify({'opinions': opinions_list}), 200


@app.route('/api/opinions/', methods=['POST'])
def add_opinion():
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage('Неверный формат запроса или пустое тело JSON')
    if 'title' not in data or 'text' not in data:
        raise InvalidAPIUsage('В запросе отсутствуют обязательные поля')
    stmt = db.select(Opinion).where(Opinion.text == data['text'])
    if db.session.scalar(stmt):
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    opinion = Opinion()
    opinion.from_dict(data)
    db.session.add(opinion)
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 201


@app.route('/api/get-random-opinion/', methods=['GET'])
def get_random_opinion():
    opinion = random_opinion()
    if opinion is not None:
        return jsonify({'opinion': opinion.to_dict()}), 200
    raise InvalidAPIUsage('В базе данных нет мнений', 404)
