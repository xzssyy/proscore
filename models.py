import datetime
import random

from app import db, app
from utilities import get_rank


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Record=Record)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    open_id = db.Column(db.String(256))

    # one-to-many
    records = db.relationship('Record', backref='user', lazy='dynamic')


class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)

    score = db.Column(db.Float)
    accuracy = db.Column(db.Float)
    fluency = db.Column(db.Float)
    completeness = db.Column(db.Float)

    time = db.Column(db.DateTime)
    rank = db.Column(db.Integer)

    # 1 item 2 test
    type = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))

    def to_json(self):
        res = {'id': self.id,
               'score': self.score,
               'accuracy': self.accuracy,
               'fluency': self.fluency,
               'completeness': self.completeness,
               'time': self.time.strftime("%m/%d/%Y, %H:%M:%S"),
               'rank': self.rank}

        return res

    @staticmethod
    def create_record(user_id, test_id):
        test = db.session.execute(db.select(Test).filter(Test.id == test_id)).scalar()
        item_count = test.item_count

        if test.test_type == 1:
            items = test.words
        else:
            items = test.sentences

        for item in items:
            record = Record(score=random.randrange(0, 101),
                            accuracy=random.randrange(0, 101),
                            fluency=random.randrange(0, 101),
                            completeness=random.randrange(0, 101),
                            user_id=user_id,
                            test_id=test_id,
                            time=datetime.datetime.now(),
                            type=1)
            record.rank = get_rank(record.score)
            db.session.add(record)

        record = Record(score=random.randrange(0, 101),
                        accuracy=random.randrange(0, 101),
                        fluency=random.randrange(0, 101),
                        completeness=random.randrange(0, 101),
                        user_id=user_id,
                        test_id=test_id,
                        time=datetime.datetime.now(),
                        type=2)

        db.session.add(record)
        db.session.commit()


class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    info = db.Column(db.Text)
    item_count = db.Column(db.Integer)
    # 1 单词 2 句子
    test_type = db.Column(db.Integer)
    # 学段
    difficult = db.Column(db.Integer)

    # one-to-many
    words = db.relationship('Word', backref='test', lazy='dynamic')
    sentences = db.relationship('Sentence', backref='test', lazy='dynamic')
    records = db.relationship('Record', backref='test', lazy='dynamic')

    def summary_user(self, user_id):
        test = db.session.execute(db.select(Test).filter(Test.id == test_id)).scalar()
        item_count = test.item_count

    def to_json(self):
        res = {'id': self.id,
               'title': self.title,
               'info': self.info,
               'item_count': self.item_count,
               'test_type': self.test_type,
               'items': [item.to_json() for item in self.sentences]
               if self.words is None else [item.to_json() for item in self.words]}

        return res


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256))
    trans_text = db.Column(db.String(256))

    # ForeignKey
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))

    def to_json(self):
        res = {'id': self.id,
               'text': self.text,
               'trans_text': self.trans_text}

        return res


class Sentence(db.Model):
    __tablename__ = 'sentences'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256))
    trans_text = db.Column(db.String(256))

    # ForeignKey
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))

    def to_json(self):
        res = {'id': self.id,
               'text': self.text,
               'trans_text': self.trans_text}

        return res
