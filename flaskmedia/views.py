from flask import request, redirect, url_for, render_template, Flask, flash, abort, jsonify, session, send_from_directory, make_response, Response,  jsonify
from flaskmedia import db, app
from flaskmedia.models import User, Media, MovieInfo

from datetime import datetime

import uuid

import os

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user, authenticated = User.authenticate(db.session.query, request.form['name'], request.form['password'])
        if authenticated:
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('media'))
        else:
            flash('Invalid inputs')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You were logged out')
    return redirect(url_for('login'))

#media
#現在、動画のみ対応している。
@app.route('/media', methods=['GET', 'POST'])
def media():
    if request.method == 'POST':
        query = request.form['query']
        if len(query) > 0:
            medias = Media.query.filter_by(user_id=session['user_id']).filter(Media.name.like('%' + query +'%'))
        else:
            medias = Media.query.filter_by(user_id=session['user_id'])   
    else:
        medias = Media.query.filter_by(user_id=session['user_id'])
    return render_template('media/list.html', medias=medias)

@app.route('/media/<int:media_id>/edit')
def edit_media(media_id):
    media = Media.query.filter_by(id=media_id).first()
    if media is None or media.user_id != session['user_id']:
        return abort(500)
    return render_template('media/edit.html', media=media)

@app.route('/media/<int:media_id>/play')
def play_media(media_id):
    media = Media.query.filter_by(id=media_id).first()
    if media is None or media.user_id != session['user_id']:
        return abort(500)
    return render_template('media/play.html', media=media)

@app.route('/media/<int:media_id>/stream')
def stream_media(media_id):
    media = Media.query.filter_by(id=media_id).first()
    if media is None or media.user_id != session['user_id']:
        return abort(500)

    print(media.file_name)
    m3u8_filename = os.path.splitext(media.file_name)[0] + ".m3u8"
    return render_template('media/stream.html', media=media, m3u8_filename=m3u8_filename)

@app.route("/media/<int:media_id>/update", methods=['POST'])
def update_media(media_id):
    media = Media.query.filter_by(id=media_id).first()
    media.name = request.form['name']
    registration_date_local_str = request.form['registration_date_local_str']
    print(registration_date_local_str)
    media.registration_date = datetime.strptime(request.form['registration_date_local_str'],"%Y-%m-%dT%H:%M")
    db.session.add(media)
    db.session.commit()

    return redirect(url_for('media'))
@app.route('/media/upload', methods=['POST'])
def upload_media():
    if request.method == 'POST':
        user_id = session['user_id']
        if user_id :
            uploaded_files = request.files.getlist("file[]")
            #file = request.files['file']
            print(uploaded_files)
            for file in uploaded_files:
                add_file(file, user_id)
            return redirect(url_for('media'))
    else:
        return abort(400)

@app.route('/api/media/upload', methods=['POST'])
def api_upload_media():
    if request.method == 'POST':
        user_id = session['user_id']
        if user_id :
            upload_file = request.files['file']
            add_file(upload_file, user_id)
            ret = {
                "result" : "OK"
            }
            return jsonify(ret)
    ret = {
        "result" : "NG"
    }
    return jsonify(ret)

def add_file(file, user_id):
    original_name = file.filename
    base_name, ext = os.path.splitext(file.filename) #拡張子ともともとのベースを分ける
    file_name = uuid.uuid4().hex + ext
    type_id = Media.TYPE_ID_MOVIE #とりあえず動画のみ

    #日付からフォルダを生成
    now = datetime.now()
    ##user_id/yyyy/MM/ddのフォルダ
    folder_path = os.path.join(str(session['user_id']),"{0:0>4}".format(now.year),"{0:0>2}".format(now.month),"{0:0>2}".format(now.day))
    media_folder_path = os.path.join(app.config['UPLOAD_HOME_FOLDER'], folder_path)
    ##フォルダを作る　重複していてもok
    os.makedirs(media_folder_path, exist_ok=True)
    #ファイルの保存
    file_save_path = os.path.join(media_folder_path, file_name)
    file.save( file_save_path )
    #DBに登録
    media = Media(original_name=original_name, file_name=file_name,user_id=user_id, folder_path=folder_path, type_id=type_id, registration_date=now)
    db.session.add(media)
    db.session.flush()
    #print('media_id',media.id)
    if type_id == Media.TYPE_ID_MOVIE: #動画の場合のメタ情報
        movie_info = MovieInfo(media_id = media.id)
        db.session.add(movie_info)
    db.session.commit()

#data access
#videoタグで使うsrcファイルを取得
#TODO URLの付け方が微妙な気がする
@app.route('/media/<int:media_id>/video_src')
def video_src(media_id):
    media = Media.query.filter_by(id=media_id).first()
    media_folder_path = os.path.join(app.config['MEDIA_FOLDER'], media.folder_path)

    if 'Range' in request.headers:
        media_file_data = open(os.path.join(media_folder_path, media.file_name), 'rb').read()
        start, end = request.headers['Range'][len('bytes='):].split('-')
        try:
            start = int(start)
        except ValueError:
            start = 0
        try:
            end = int(end)
        except ValueError:
            end = len(media_file_data)
        response = Response(media_file_data[start:end], mimetype='video/mp4', status=206)
        response.headers.add_header('Content-Range', 'bytes {0}-{1}/{2}'.format(start, end-1, len(media_file_data)))
    else:
        response = make_response(send_from_directory(media_folder_path, media.file_name, as_attachment=True, mimetype='video/mp4'))
    return response

@app.route('/media/<int:media_id>/stream/<filename>')
def stream_src(media_id, filename):
    '''
    stream用のファイルを取得する
    filenameがm3u8で終わるときと。tsで終わるときで処理を複数にする必要がある？
    '''
    media = Media.query.filter_by(id=media_id).first()
    stream_file_folder_path = os.path.join(app.config['STREAM_FOLDER'], str(media_id))
    print(stream_file_folder_path)
    return send_from_directory(stream_file_folder_path, filename, mimetype="application/x-mpegURL")

@app.route('/media/<int:media_id>/download')
def download_media(media_id):
    '''
    DBで指定した名前でファイルをダウンロードする
    '''
    media = Media.query.filter_by(id=media_id).first()
    media_folder_path = os.path.join(app.config['MEDIA_FOLDER'], media.folder_path)

    return send_from_directory(media_folder_path, media.file_name, as_attachment=True, attachment_filename=media.name.encode("utf-8"))

@app.route('/media/<int:media_id>/delete/')
def delete_media(media_id):
    if session['user_id']:
        media = Media.query.filter_by(id=media_id, user_id=session['user_id']).first()
        if media:
            movie_info = MovieInfo.query.filter_by(media_id = media_id).first()
            if movie_info:
                db.session.delete(movie_info)
            file_path = os.path.join(app.config['MEDIA_FOLDER'], media.folder_path, media.file_name)
            os.remove(file_path)
            db.session.delete(media)
            db.session.commit()

            return redirect(url_for('media'))
    return abort(500)

#user maintenance
@app.route('/users/')
def user_list():
    users = User.query.all()
   
    return render_template('user/list.html', users=users)

@app.route('/users/<int:user_id>')
def user_detail(user_id):
    user = User.query.get(user_id)
    return render_template('user/detail.html', user=user)

@app.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
def user_edit(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    if request.method == 'POST':
        user.name = request.form['name']
        user.password = request.form['password']
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_detail', user_id=user_id))
    return render_template('user/edit.html', user=user)

@app.route('/users/create/', methods=['GET', 'POST'])
def user_create():
    if request.method == 'POST':
        user = User(name=request.form['name'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_list'))
    return render_template('user/edit.html')


@app.route('/users/<int:user_id>/delete/', methods=['POST'])
def user_delete(user_id):
    user = User.query.get(user_id)
    if user is None:
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response
    db.session.delete(user)
    db.session.commit()
    return jsonify({'status': 'OK'})