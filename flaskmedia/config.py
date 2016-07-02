#configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/media.db' #manage.pyの下のflaskmediaフォルダ以下にdataフォルダがあると仮定
UPLOAD_HOME_FOLDER = "/flaskmedia/data" #manage.pyからの相対パス
MEDIA_FOLDER = "/flaskmedia/data" #1番目のflaskmediaからの相対パス 上と同じフォルダなので、統一したい
STREAM_FOLDER = "/flaskmedia/stream"
DEBUG = True
SECRET_KEY = 'secret key'
