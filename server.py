from flask import Flask, request, redirect, flash, session
from flask import render_template, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, logout_user, login_required
from user import User

from werkzeug.utils import secure_filename

import numpy as np
import mysql.connector
from termcolor import colored
import cv2

import os
import shutil
import re
import string
from datetime import datetime
import random
from PIL import Image

from doll_model import pred_price

UPLOAD_FOLDER = 'static/image/history'
TMP_FOLDER = 'static/image/tmp'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'JPG'])
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TMP_FOLDER'] = TMP_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)

# 接続
#conn = mysql.connector.connect(
#    host='127.0.0.1',
#    port=8080,
#    user='root',
#    password='',
#    database='fringe'
#)

# 拡張子の検証
def allowed_file(filename):
    # .が存在するか検証
    # 許可された拡張子なら1を、そうでなければ0を返す
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ランダムにメッセージを選択
def picked_up():
    messages = [
        "こんにちは",
        "どうも",
        "やぁ"
    ]
    return np.random.choice(messages)

@app.route('/sample')
def sample():
    return render_template('sample.html')

# indexにアクセスした時の処理
@app.route('/')
def index():
    return redirect('/uploader')
    title = "ようこそ"
    message = picked_up()

    return render_template('index.html', message=message, title=title)

# ログイン
@app.route('/login', methods=['GET'])
def form():
    return render_template('login.html')

# ログイン処理
@app.route('/login', methods=['POST'])
def login():
    user = User()
    login_user(user)
    return redirect(url_for('dashboard'))

# ログアウト
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# ダッシュボード表示
@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@login_manager.user_loader
def load_user(user_id):
    return User()

# 鑑定
@app.route('/uploader', methods=['GET', 'POST'])
def uploads_file():
    #tmpフォルダを空にする
    shutil.rmtree(os.path.join(app.config['TMP_FOLDER']))
    os.mkdir(os.path.join(app.config['TMP_FOLDER']))

    # リクエストがPOSTかどうかの判別
    if request.method == 'POST':
        # ファイルがなかった場合
        if 'file' not in request.files:
            app.logger.debug(colored('ファイルがありません!', 'red'))
            app.logger.debug(colored(request.files, 'red'))
            flash('ファイルブラウザを認識できませんでした', 'success')
            return redirect(request.url)
        
        # ファイルのリストを取り出し
        files = request.files.getlist('file')
        price_list = []
        image_list = []

        for f, i in zip(files, range(len(files))):
            # ファイルが選択されていない場合
            if f.filename == '':
                app.logger.debug(colored('ファイルが選択されていません！', 'red'))
                flash('ファイルを選択してください', 'danger')
                return redirect(request.url)
            # 拡張子は許可されたものか？
            if f and allowed_file(f.filename):
                app.logger.debug(colored('許可された拡張子です！', 'green'))
                # 危険な文字を削除（サニタイズ処理）
                filename = secure_filename(f.filename)
                # ファイルを保存
                date_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_") + str(i) + '_' + ''.join([random.choice(string.ascii_letters + string.digits) for i in range(5)])
                #save_path = os.path.join(app.config['UPLOAD_FOLDER'], date_now + '.png')
                #f.save(save_path)

                #--------------------------------------------------------------
                # 画像として読み込み
                stream = f.stream
                img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8) # numpy配列に変換
                #app.logger.debug(colored(img_array, 'yellow'))
                img = cv2.imdecode(img_array, 3) # shapeを変更
                #app.logger.debug(colored(img, 'red'))

                # 画像の解像度を変更
                resize_width = 1024
                img = Image.fromarray(np.uint8(img)) # numpyからPILへ変換
                img_width, img_height = img.size # 画像の解像度を取得
                resize_height = resize_width / img_width * img_height # 指定した幅に対する高さを計算
                img = img.resize((int(resize_width), int(resize_height))) # 変換
                img = np.array(img) # PILからnumpyへ変換
                
                # 予測
                price = pred_price(img) # 価格を予測
                app.logger.debug(colored(price, 'blue'))

                # 保存
                #date_now = str(int(price[0])).zfill(8)+ '_' + datetime.now().strftime("%Y_%m_%d_%_H_%M_%S_") + str(i) + '_' + ''.join([random.choice(string.ascii_letters + string.digits) for i in range(5)])
                date_now = str(int(price[0])).zfill(8) + '_' + datetime.now().strftime("%Y_%m_%d_%_H_%M_%S_")
                save_path = os.path.join(app.config['TMP_FOLDER'], date_now + ".png")
                cv2.imwrite(save_path, img)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], date_now + ".png")
                cv2.imwrite(save_path, img)
                #--------------------------------------------------------------

            else:
                app.logger.debug(colored('許可されていない拡張子が含まれていました！', 'red'))
                flash('許可されていない拡張子が含まれていました', 'danger')
                return redirect(request.url)
        flash('鑑定完了しました！', 'success')

    image_list = os.listdir(TMP_FOLDER)[::-1]
    price_list = ["{:,}".format(int(re.match(r'[0-9]{8}', i).group(0))) for i in image_list] # 落札価格を読み取る
    image_list2 = os.listdir(UPLOAD_FOLDER)[::-1]
    price_list2 = ["{:,}".format(int(re.match(r'[0-9]{8}', i).group(0))) for i in image_list2] # 落札価格を読み取る    
    #price_list = [100 for i in image_list] # とりあえず全部100円で表示

    return render_template('uploader.html', images=zip(image_list, price_list), images2=zip(image_list2, price_list2))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['TMP_FOLDER'], filename)


# /postにアクセスした時の処理
@app.route('/post', methods=['GET', 'POST'])
def post():
    title = "こんにちは"
    if request.method == 'POST':
        name = request.form['name']
        return render_template('form.html', name=name, title=title)
    else:
        #indexにアクセス
        return redirect(url_for('index'))

@app.route('/hello')
def hello():
    message = 'sample_string'
    message_dic = {}
    message_dic['name'] = 'hogehoge'
    message_dic['pass'] = 'fugafuga'
    return render_template('hello_world.html', message=message, message_dic=message_dic)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
