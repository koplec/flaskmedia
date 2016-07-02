from sqlalchemy import Column, String, Integer, Unicode, UnicodeText, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import synonym
from datetime import datetime

from werkzeug import check_password_hash, generate_password_hash
from flaskmedia import db

class User(db.Model):
	'''
	User
	'''
	__tablename__ = "users"
	id = Column(Integer, primary_key=True)
	name = Column(String(255), unique=True,nullable=False)
	_password = Column('password', String(100), nullable=False)#passwordというカラム

	def _get_password(self):
		return self._password
	def _set_password(self, password):
		if password:
			password = password.strip()
		self._password = generate_password_hash(password)
	password_descriptor = property(_get_password, _set_password)
	password = synonym('_password', descriptor=password_descriptor)

	def check_password(self, password):
		password = password.strip()
		if not password:
			return False
		return check_password_hash(self.password, password)

	@classmethod
	def authenticate(cls, query, name, password):
		user = query(cls).filter(cls.name == name).first()
		if user is None:
			return None, False
		return user, user.check_password(password)

	def __repr__(self):
		return u'<User id={self.id} name={self.name}>'.format(self=self)

class Media(db.Model):
	'''
	Media
	'''
	__tablename__ = "medias"
	id = Column(Integer, primary_key=True)
	original_name = Column(String(255),nullable=False) #アップロード時のもともとのファイル名
	file_name = Column(String(255),nullable=False) #アップロード時にサーバ側で保管するファイル名（拡張子はそのまま　ファイル名を自動生成する）
	name = Column(String(255), nullable=False) #表示するための名前
	user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
	user = db.relationship('User', backref=db.backref('medias', lazy='dynamic'))
	folder_path = Column(String(255), nullable=False)
	registration_date = Column(DateTime) #登録日
	type_id = Column(Integer, nullable=False) #動画、画像、音楽、文書（再生するアプリの種類を選択するためのもの）
	create_date = Column(DateTime) #このシステムでの作成日 フォルダパスと一致する

	#TYPE_IDが取る値
	TYPE_ID_MOVIE = 1

	def __init__(self, original_name, file_name, user_id, folder_path, type_id, registration_date=None):
		self.original_name = original_name
		self.name = original_name
		self.file_name = file_name
		self.user_id = user_id
		self.folder_path = folder_path
		self.type_id = type_id
		if registration_date is None:
			registration_date = datetime.today()
		
		self.registration_date = registration_date
		self.create_date = datetime.today()


	def __repr__(self):
		return u'<Media id={self.id} name={self.name}>'.format(self=self)

class MovieInfo(db.Model):
	'''
	動画に紐づく情報のみを取得
	'''
	__tablename__ = "movie_infos"
	id = Column(Integer , primary_key=True)
	media_id = Column(Integer, ForeignKey('medias.id'), nullable=False)
	media = db.relationship('Media', backref=db.backref('medias'))
	make_m3u8_count = Column(Integer, nullable=False,default=0)
	m3u8_create_datetime = Column(DateTime)
	m3u8_delete_datetime = Column(DateTime)
	play_count = Column(Integer, nullable=False, default=0)

	def __init__(self, media_id):
		self.media_id = media_id
	
	def __repr__(self):
		return u'<MovieInfo id={self.id} media_id={self.media_id}>'.format(self=self)

def init():
	db.create_all()
