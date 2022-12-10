import requests
from flask import request, jsonify
from sqlalchemy import and_, desc

from app import app, db
from microsoft_api import get_pronScore
from models import User, Test, Record

"""
    GET METHODS
"""


@app.route('/')
def hello_world():
    return 'Hello Wold from xzssyy'


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


# 获取record,用于访问 *指定test的record*  *答题完成后的试卷结果*
@app.route('/user/<string:open_id>/test/<string:test_id>/record')
def get_record(open_id, test_id):
    user = db.session.execute(db.select(User).filter(User.open_id == open_id)).scalar()
    test = db.session.execute(db.select(Test).filter(Test.id == test_id)).scalar()
    new_records = user.records.filter(and_(Record.test_id == test_id,
                                           Record.type == 1,
                                           Record.status == 0)).all()

    if len(new_records) == test.item_count:
        # 删除旧记录
        old_records = user.records.filter(and_(Record.test_id == test_id,
                                               Record.status == 1)).all()
        for i in old_records:
            db.session.delete(i)
        db.session.commit()

        # 生成最新test记录
        new_test_record = Record.generate_test_record(test_id, user.id, new_records)

        for i in new_records:
            i.status = 1

        new_test_record.status = 1
        db.session.commit()

        return jsonify(new_test_record.to_json())
    else:
        record = user.records.filter(and_(Record.test_id == test_id,
                                          Record.type == 2,
                                          Record.status == 1)).first()
        return jsonify(record.to_json() if record else {'error': 'record is None'})


@app.route('/user/<string:open_id>/records')
def get_records(open_id):
    user = db.session.execute(db.select(User).filter(User.open_id == open_id)).scalar()
    records = user.records.filter(and_(Record.type == 2, Record.status == 1))

    return jsonify({'items': [record.to_json() for record in records]})


@app.route('/test/<string:test_id>/rank_list')
def get_rank_list(test_id):
    score = int(request.args.get('score'))
    record_up = db.session.execute(
        db.select(Record).filter(and_(Record.score > score, Record.test_id == test_id, Record.type == 2)).order_by(
            desc(Record.score))).scalar()

    record_down = db.session.execute(
        db.select(Record).filter(and_(Record.score < score, Record.test_id == test_id, Record.type == 2)).order_by(
            Record.score)).scalar()

    user_up = record_up.user if record_up else None
    user_down = record_down.user if record_down else None

    return jsonify({
        'up': {
            'user': user_up.open_id if user_up else None,
            'score': record_up.score if record_up else None
        }
        ,
        'down': {
            'user': user_down.open_id if user_down else None,
            'score': record_down.score if record_down else None
        }
    })


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

    if user is None:
        user = User(open_id=res['openid'])
        db.session.add(user)
        db.session.commit()

    return jsonify(res)


@app.route('/user/<string:open_id>/records/add', methods=['POST'])
def add_item_record(open_id):
    test_id = request.args.get('test_id')
    item_id = request.args.get('item_id')

    file = request.files.get('voice.wav')

    if file is None:
        return jsonify({'error': 'file not found'})

    test = db.session.execute(db.select(Test).filter(Test.id == test_id)).scalar()
    item = test.get_items(item_id)
    user = db.session.execute(db.select(User).filter(User.open_id == open_id)).scalar()

    # file = open('录音.wav', 'rb')
    res = get_pronScore(file, item.text)["NBest"][0]

    record = Record.generate_item_record(res, user.id, test_id, item_id)

    return jsonify(record.to_json())
