Userを作成
http://study-flask.readthedocs.io/ja/latest/04.html


m3u8の作り方
ffmpeg -i 3a8bd18520fd4fb4b0af6fa7cffdad1b.mp4  -vcodec libx264 -acodec aac -strict -2 -flags +loop-global_header -bsf h264_mp4toannexb -f segment -segment_format mpegts -segment_time 10 -segment_list 3a8bd18520fd4fb4b0af6fa7cffdad1b.m3u8 3a8bd18520fd4fb4b0af6fa7cffdad1b_%04d.ts

動かし方
python3 manage.py runserver --threaded --host=0.0.0.0

バックアップ
USB+HDD (1TB)をつけているので、こんな感じ
ln -s /media/fumitaka/Flaskmedia_Backu/ backup
rsync -av data backup/

