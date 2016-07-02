from __future__ import print_function
from flask_script import Manager

from flaskmedia import app, db
from flaskmedia.models import Media, MovieInfo

import os
import subprocess
from datetime import datetime

manager = Manager(app)

@manager.command
def init_db():
    db.create_all()

@manager.command
def create_stream_file(media_id):
    media_id = int(media_id)
    media  = Media.query.filter_by(id=media_id).first()
    
    print("BEGIN creating stream files %d" % media_id)
    base_name, ext = os.path.splitext(media.file_name)

    input_file = os.path.join(app.config['MEDIA_FOLDER'], media.folder_path, media.file_name)
    output_folder = os.path.join(app.config['STREAM_FOLDER'], str(media.id))
    os.makedirs(output_folder, exist_ok=True)
    output_m3u8 = os.path.join(output_folder, base_name + ".m3u8")
    output_ts = os.path.join(output_folder, base_name + "_%05d.ts")
    ffmpeg_cmd = "ffmpeg -i {0}  -vcodec libx264 -acodec aac -strict -2 -flags +loop-global_header -bsf h264_mp4toannexb -f segment -segment_format mpegts -segment_time 10 -segment_list {1} {2}".format(input_file, output_m3u8, output_ts)
    subprocess.call(ffmpeg_cmd, shell=True)
    print("END creating stream files")
    movie_info = MovieInfo.query.filter_by(media_id=media.id).first()
    movie_info.m3u8_create_datetime = datetime.today()
    movie_info.make_m3u8_count += 1
    db.session.add(movie_info)
    db.session.commit()

if __name__ == '__main__':
    manager.run()
