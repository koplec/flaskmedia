from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# from_object()は、与えられたオブジェクトのうち、大文字の変数をすべて取得する
app.config.from_object('flaskmedia.config')

db = SQLAlchemy(app)

import flaskmedia.views