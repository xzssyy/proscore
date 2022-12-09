from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://xzssyy:Py20021023@xzssyysql.mysql.database.azure.com:3306/proscore?' \
                                 'ssl_ca=DigiCertGlobalRootCA.crt.pem'

app.config['appid'] = 'wxf8b6aeb0b0cdc0b8'
app.config['secret'] = '67102d804cd4b90011af5d1537b4668d'

db = SQLAlchemy(app)
Migrate(app, db)



import api



if __name__ == '__main__':
    app.run()
