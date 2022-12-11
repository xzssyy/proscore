import datetime
import random

from sqlalchemy import and_

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
    item_id = db.Column(db.Integer)

    # 0 wait 1 finish
    status = db.Column(db.Integer, default=0)

    def to_json(self):
        res = {'id': self.id,
               'user_id': self.user_id,
               'test_id': self.test_id,
               'item_id': self.item_id,
               'type': self.type,
               'score': self.score,
               'accuracy': self.accuracy,
               'fluency': self.fluency,
               'completeness': self.completeness,
               'time': self.time.strftime("%m/%d/%Y, %H:%M:%S"),
               'rank': self.rank,
               'test_title': self.test.title}

        return res

    @staticmethod
    def generate_item_record(res, user_id, test_id, item_id):
        # 判断答题中是否重复提交
        record = db.session.execute(db.select(Record).filter(and_(Record.test_id == test_id,
                                                                  Record.user_id == user_id,
                                                                  Record.item_id == item_id,
                                                                  Record.status == 0))
                                    ).scalar()

        if record:
            record.score = int(res['PronScore'])
            record.accuracy = int(res['AccuracyScore'])
            record.fluency = int(res['FluencyScore'])
            record.completeness = int(res['CompletenessScore'])
            record.rank = get_rank(record.score)
            record.time = datetime.datetime.now()
        else:
            record = Record(score=int(res['PronScore']),
                            accuracy=int(res['AccuracyScore']),
                            fluency=int(res['FluencyScore']),
                            completeness=int(res['CompletenessScore']),
                            user_id=user_id,
                            time=datetime.datetime.now(),
                            type=1,
                            item_id=item_id,
                            test_id=test_id)
            record.rank = get_rank(record.score)
            db.session.add(record)

        db.session.commit()
        return record

    @staticmethod
    def generate_test_record(test_id, user_id, items):
        score = sum(item.score for item in items) // len(items)
        accuracy = sum(item.accuracy for item in items) // len(items)
        fluency = sum(item.fluency for item in items) // len(items)
        completeness = sum(item.completeness for item in items) // len(items)

        record = Record(score=score,
                        accuracy=accuracy,
                        fluency=fluency,
                        completeness=completeness,
                        user_id=user_id,
                        test_id=test_id,
                        time=datetime.datetime.now(),
                        type=2,
                        status=0)
        record.rank = get_rank(record.score)

        db.session.add(record)
        db.session.commit()
        return record

    """
        for test
    """

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
                            type=1,
                            item_id=item.id)

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
    image = db.relationship('Image', lazy='immediate')

    def to_json(self):
        res = {'id': self.id,
               'title': self.title,
               'info': self.info,
               'item_count': self.item_count,
               'test_type': self.test_type,
               'thumb_url': 'static/' + str(self.image[0].image_name),
               'items': [item.to_json() for item in self.sentences]
               if self.words.count() == 0 else [item.to_json() for item in self.words]}

        return res

    def get_items(self, item_id):
        if self.test_type == 1:
            return self.words.filter(Word.id == item_id).scalar()
        else:
            return self.sentences.filter(Sentence.id == item_id).scalar()


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


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))
    image_name = db.Column(db.String(64))
