from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from datetime import datetime, timedelta
import certifi
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler

ca = certifi.where()

client = MongoClient('mongodb+srv://account:password@')

SECRET_KEY = 'password'

db = client.dbsparta

app = Flask(__name__)

m = hashlib.sha256()

sched = BackgroundScheduler(daemon=True)


@app.before_request
def before_request():
    scheme = request.headers.get('X-Forwarded-Proto')
    if scheme and scheme == 'http' and request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/movie')
def movies():
    return render_template('movie.html')

@app.route("/movie2", methods=["GET"])
def movie_get():
    movie_list = list(db.movies.find({}, {'_id': False}))
    return jsonify({'movies': movie_list})

@app.route('/movies', methods=['POST'])
def movieswrite():
    nick = request.form['nick_give']
    name_receive = nick.strip('name=')
    print(name_receive)
    comment_receive = request.form['comment_give']
    movieNumber_receive = request.form['movieNumber_give']
    db.moviewrite.insert_one({'name':name_receive,'comment':comment_receive,'movieNumber':movieNumber_receive})
    return jsonify({'msg': '등록완료!!'})

@app.route("/moviewrite", methods=["GET"])
def moviewrite_get():
    moviewrite_list = list(db.moviewrite.find({}, {'_id': False}))
    return jsonify({'moviewrite': moviewrite_list})

@app.route("/movie1", methods=["GET"])
def get_list():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.naver', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    trs = soup.select('#old_content > table > tbody > tr')

    rank = 0;

    db.movieinfo.drop()
    for tr in trs:
        movieinfo = tr.select_one('td.title > div > a')
        if movieinfo is not None:
            title = movieinfo.text
            link = movieinfo['href']

            rank = rank + 1

            doc = {
                'title': title,
                'link': 'https://movie.naver.com' + link,
                'rank': rank
            }

            db.movieinfo.insert_one(doc)

    url = list(db.movieinfo.find({}, {'_id': 0, 'title': 0}))

    db.movies.drop()
    for i in url:
        text = i['link']
        rank = i['rank']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(text, headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')
        image = soup.select_one('meta [property="og:image"]')['content']
        title = soup.select_one('meta [property="og:title"]')['content']
        desc = soup.select_one('#content > div.article > div.section_group.section_group_frst > div:nth-child(1) > div > div.story_area > p')
        if desc is not None:
            desc1 = soup.select_one('meta [property="og:description"]')['content']

            doc = {
                'rank': rank,
                'title': title,
                'image': image,
                'desc': desc.text,
                'desc1': desc1
            }
            db.movies.insert_one(doc)


        else :
            doc = {
                'rank': rank,
                'title': title,
                'image': image,
                'desc': '줄거리가 아직 등록되지 않았어요!',
                'desc1': '줄거리가 아직 등록되지 않았어요!'
            }
            db.movies.insert_one(doc)

    sched.start()

    return jsonify({'result': 'success'})


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/login')
def login():
    return render_template('login.html')





@app.route('/signup', methods=['POST'])
def signup_success():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


@app.route('/api/login', methods=['POST'])
def user_login():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.user.find_one({'id': username_receive, 'pw': password_hash})
    name = result['nick']

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token , 'nick':name})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디와 비밀번호가 일치하지 않습니다.'})


@app.route('/api/user_check', methods=['POST'])
def user_check():
    username_receive = request.form['username_give']
    exist = bool(db.user.find_one({"id": username_receive}))
    return jsonify({'result': 'success', 'exist': exist})

sched.add_job(get_list, 'cron', hour='12', minute='30',timezone='Asia/Seoul')
sched.start()


if __name__ == '__main__':

    app.run('0.0.0.0', port=8000, debug=True)


