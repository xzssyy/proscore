import datetime

import requests
from flask import request, jsonify

from app import app, db
from models import User, Test, Record

"""
    GET METHODS
"""


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/tests')
def get_tests():
    has_items = request.args.get('has_items')
    tests = db.session.execute(db.select(Test)).scalars()

    tests_json = [test.to_json() for test in tests]

    if has_items is None or not bool(has_items):
        for test in tests_json:
            test.pop('items')

    return jsonify({'items': tests_json})


@app.route('/test/<string:id>')
def get_test(id):
    test = db.session.execute(db.select(Test).filter(Test.id == id)).scalar()
    return jsonify(test.to_json())


@app.route('/test/<string:id>/picture')
def get_test_picture(id):
    pass


@app.route('/user/<string:open_id>/records')
def get_records(open_id):
    user = db.session.execute(db.select(User).filter(User.open_id == open_id)).scalar()
    records = user.records.filter(Record.type == 2)

    return jsonify({'items': [record.to_json() for record in records]})




"""
    POST METHODS
"""


@app.route('/login', methods=['POST'])
def login():
    code = request.args.get('code')
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    response = requests.request('GET', url, params={'appid': app.config['appid'],
                                                    'secret': app.config['secret'],
                                                    'js_code': code,
                                                    'grant_type': 'authorization_code'})

    res = response.json()
    try:
        user = db.session.execute(db.select(User).filter(User.open_id == res['openid']))
    except:
        return jsonify({'info': 'error'})

    if user is not None:
        user = User(open_id=res['openid'])
        db.session.add(user)
        db.session.commit()

    return jsonify(res)

#
# @app.route('/test/<string:id>/picture')
# def get_test_picture(id):
#     pass
