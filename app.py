import os
import sys
import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import request, redirect, url_for
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from pandas import read_sql_query
from sqlalchemy.sql import text
from sqlalchemy import func



WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.secret_key = 'Wangyun030425'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# 模型定义
class MovieInfo(db.Model):
    __tablename__ = 'movie_info'
    movie_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ##movie_id = db.Column(db.String(10), primary_key=True)
    movie_name = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.DateTime)
    country = db.Column(db.String(20))
    genre = db.Column(db.String(10))
    year = db.Column(db.Integer, nullable=False)
    director = db.Column(db.String(255))  # 导演
    box_office = db.relationship('MoveBox', backref='movie', uselist=False)


class MoveBox(db.Model):
    __tablename__ = 'move_box'
    movie_id = db.Column(db.Integer, db.ForeignKey('movie_info.movie_id'), primary_key=True)
    box = db.Column(db.Float)

class ActorInfo(db.Model):
    __tablename__ = 'actor_info'
    actor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ##actor_id = db.Column(db.String(10), primary_key=True)
    actor_name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(2), nullable=False)
    country = db.Column(db.String(20))

class MovieActorRelation(db.Model):
    __tablename__ = 'movie_actor_relation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 修改为自动增长
    movie_id = db.Column(db.String(10), db.ForeignKey('movie_info.movie_id'), nullable=False)
    actor_id = db.Column(db.String(10), db.ForeignKey('actor_info.actor_id'), nullable=False)
    relation_type = db.Column(db.String(20))
# 初始化数据库的命令


@app.cli.command('init-db')
def init_db():
    db.create_all()
    print("Database initialized.")
@app.cli.command('clear-db')
def clear_db():
    """Clears all data from the database tables."""
    db.session.query(MovieInfo).delete()
    db.session.query(MoveBox).delete()
    db.session.query(ActorInfo).delete()
    db.session.query(MovieActorRelation).delete()
    db.session.commit()
    print("All tables cleared.")
@app.cli.command('populate-db')
def populate_db():

    movies_data = [
        {'movie_id': '1001', 'movie_name': '战狼2', 'release_date': '2017-07-27', 'country': '中国', 'genre': '战争', 'year': 2017},
        {'movie_id': '1002', 'movie_name': '哪吒之魔童降世', 'release_date': '2019-07-26', 'country': '中国', 'genre': '动画', 'year': 2019},
        {'movie_id': '1003', 'movie_name': '流浪地球', 'release_date': '2019-02-05', 'country': '中国', 'genre': '科幻', 'year': 2019},
        {'movie_id': '1004', 'movie_name': '复仇者联盟4', 'release_date': '2019-04-24', 'country': '美国', 'genre': '科幻', 'year': 2019},
        {'movie_id': '1005', 'movie_name': '红海行动', 'release_date': '2018-02-16', 'country': '中国', 'genre': '战争', 'year': 2018},
        {'movie_id': '1006', 'movie_name': '唐人街探案2', 'release_date': '2018-02-16', 'country': '中国', 'genre': '喜剧', 'year': 2018},
        {'movie_id': '1007', 'movie_name': '我不是药神', 'release_date': '2018-07-05', 'country': '中国', 'genre': '喜剧', 'year': 2018},
        {'movie_id': '1008', 'movie_name': '中国机长', 'release_date': '2019-09-30', 'country': '中国', 'genre': '剧情', 'year': 2019},
        {'movie_id': '1009', 'movie_name': '速度与激情8', 'release_date': '2017-04-14', 'country': '美国', 'genre': '动作', 'year': 2017},
        {'movie_id': '1010', 'movie_name': '西虹市首富', 'release_date': '2018-07-27', 'country': '中国', 'genre': '喜剧', 'year': 2018},
        {'movie_id': '1011', 'movie_name': '复仇者联盟3', 'release_date': '2018-05-11', 'country': '美国', 'genre': '科幻', 'year': 2018},
        {'movie_id': '1012', 'movie_name': '捉妖记2', 'release_date': '2018-02-16', 'country': '中国', 'genre': '喜剧', 'year': 2018},
        {'movie_id': '1013', 'movie_name': '八佰', 'release_date': '2020-08-21', 'country': '中国', 'genre': '战争', 'year': 2020},
        {'movie_id': '1014', 'movie_name': '姜子牙', 'release_date': '2020-10-01', 'country': '中国', 'genre': '动画', 'year': 2020},
        {'movie_id': '1015', 'movie_name': '我和我的家乡', 'release_date': '2020-10-01', 'country': '中国', 'genre': '剧情', 'year': 2020},
        {'movie_id': '1016', 'movie_name': '你好，李焕英', 'release_date': '2021-02-12', 'country': '中国', 'genre': '喜剧', 'year': 2021},
        {'movie_id': '1017', 'movie_name': '长津湖', 'release_date': '2021-09-30', 'country': '中国', 'genre': '战争', 'year': 2021},
        {'movie_id': '1018', 'movie_name': '速度与激情9', 'release_date': '2021-05-21', 'country': '美国', 'genre': '动作', 'year': 2021}
    ]


    box_office_data = [
        {'movie_id': '1001', 'box': 56.84},
        {'movie_id': '1002', 'box': 50.15},
        {'movie_id': '1003', 'box': 46.86},
        {'movie_id': '1004', 'box': 42.5},
        {'movie_id': '1005', 'box': 36.5},
        {'movie_id': '1006', 'box': 33.97},
        {'movie_id': '1007', 'box': 31},
        {'movie_id': '1008', 'box': 29.12},
        {'movie_id': '1009', 'box': 26.7},
        {'movie_id': '1010', 'box': 25.47},
        {'movie_id': '1011', 'box': 23.9},
        {'movie_id': '1012', 'box': 22.37},
        {'movie_id': '1013', 'box': 30.10},
        {'movie_id': '1014', 'box': 16.02},
        {'movie_id': '1015', 'box': 28.29},
        {'movie_id': '1016', 'box': 54.13},
        {'movie_id': '1017', 'box': 53.48},
        {'movie_id': '1018', 'box': 13.92},
    ]

    actors_data = [
        {'actor_id': '2001', 'actor_name': '吴京', 'gender': '男', 'country': '中国'},
        {'actor_id': '2002', 'actor_name': '饺子', 'gender': '男', 'country': '中国'},
        {'actor_id': '2003', 'actor_name': '屈楚萧', 'gender': '男', 'country': '中国'},
        {'actor_id': '2004', 'actor_name': '郭帆', 'gender': '男', 'country': '中国'},
        {'actor_id': '2005', 'actor_name': '乔罗素', 'gender': '男', 'country': '美国'},
        {'actor_id': '2006', 'actor_name': '小罗伯特·唐尼', 'gender': '男', 'country': '美国'},
        {'actor_id': '2007', 'actor_name': '克里斯·埃文斯', 'gender': '男', 'country': '美国'},
        {'actor_id': '2008', 'actor_name': '林超贤', 'gender': '男', 'country': '中国'},
        {'actor_id': '2009', 'actor_name': '张译', 'gender': '男', 'country': '中国'},
        {'actor_id': '2010', 'actor_name': '黄景瑜', 'gender': '男', 'country': '中国'},
        {'actor_id': '2011', 'actor_name': '陈思诚', 'gender': '男', 'country': '中国'},
        {'actor_id': '2012', 'actor_name': '王宝强', 'gender': '男', 'country': '中国'},
        {'actor_id': '2013', 'actor_name': '刘昊然', 'gender': '男', 'country': '中国'},
        {'actor_id': '2014', 'actor_name': '文牧野', 'gender': '男', 'country': '中国'},
        {'actor_id': '2015', 'actor_name': '徐峥', 'gender': '男', 'country': '中国'},
        {'actor_id': '2016', 'actor_name': '刘伟强', 'gender': '男', 'country': '中国'},
        {'actor_id': '2017', 'actor_name': '张涵予', 'gender': '男', 'country': '中国'},
        {'actor_id': '2018', 'actor_name': 'F·加里·格雷', 'gender': '男', 'country': '美国'},
        {'actor_id': '2019', 'actor_name': '范·迪塞尔', 'gender': '男', 'country': '美国'},
        {'actor_id': '2020', 'actor_name': '杰森·斯坦森', 'gender': '男', 'country': '美国'},
        {'actor_id': '2021', 'actor_name': '闫非', 'gender': '男', 'country': '中国'},
        {'actor_id': '2022', 'actor_name': '沈腾', 'gender': '男', 'country': '中国'},
        {'actor_id': '2023', 'actor_name': '安东尼·罗素', 'gender': '男', 'country': '美国'},
        {'actor_id': '2024', 'actor_name': '克里斯·海姆斯沃斯', 'gender': '男', 'country': '美国'},
        {'actor_id': '2025', 'actor_name': '许诚毅', 'gender': '男', 'country': '中国'},
        {'actor_id': '2026', 'actor_name': '梁朝伟', 'gender': '男', 'country': '中国'},
        {'actor_id': '2027', 'actor_name': '白百何', 'gender': '女', 'country': '中国'},
        {'actor_id': '2028', 'actor_name': '井柏然', 'gender': '男', 'country': '中国'},
        {'actor_id': '2029', 'actor_name': '管虎', 'gender': '男', 'country': '中国'},
        {'actor_id': '2030', 'actor_name': '王千源', 'gender': '男', 'country': '中国'},
        {'actor_id': '2031', 'actor_name': '姜武', 'gender': '男', 'country': '中国'},
        {'actor_id': '2032', 'actor_name': '宁浩', 'gender': '男', 'country': '中国'},
        {'actor_id': '2033', 'actor_name': '葛优', 'gender': '男', 'country': '中国'},
        {'actor_id': '2034', 'actor_name': '范伟', 'gender': '男', 'country': '中国'},
        {'actor_id': '2035', 'actor_name': '贾玲', 'gender': '女', 'country': '中国'},
        {'actor_id': '2036', 'actor_name': '张小斐', 'gender': '女', 'country': '中国'},
        {'actor_id': '2037', 'actor_name': '陈凯歌', 'gender': '男', 'country': '中国'},
        {'actor_id': '2038', 'actor_name': '徐克', 'gender': '男', 'country': '中国'},
        {'actor_id': '2039', 'actor_name': '易烊千玺', 'gender': '男', 'country': '中国'},
        {'actor_id': '2040', 'actor_name': '林诣彬', 'gender': '男', 'country': '美国'},
        {'actor_id': '2041', 'actor_name': '米歇尔·罗德里格兹', 'gender': '女', 'country': '美国'},
]


    movie_actor_relations = [
        {'id': '1', 'movie_id': '1001', 'actor_id': '2001', 'relation_type': '主演'},
        {'id': '2', 'movie_id': '1001', 'actor_id': '2001', 'relation_type': '导演'},
        {'id': '3', 'movie_id': '1002', 'actor_id': '2002', 'relation_type': '导演'},
        {'id': '4', 'movie_id': '1003', 'actor_id': '2001', 'relation_type': '主演'},
        {'id': '5', 'movie_id': '1003', 'actor_id': '2003', 'relation_type': '主演'},
        {'id': '6', 'movie_id': '1003', 'actor_id': '2004', 'relation_type': '导演'},
        {'id': '7', 'movie_id': '1004', 'actor_id': '2005', 'relation_type': '导演'},
        {'id': '8', 'movie_id': '1004', 'actor_id': '2006', 'relation_type': '主演'},
        {'id': '9', 'movie_id': '1004', 'actor_id': '2007', 'relation_type': '主演'},
        {'id': '10', 'movie_id': '1005', 'actor_id': '2008', 'relation_type': '导演'},
        {'id': '11', 'movie_id': '1005', 'actor_id': '2009', 'relation_type': '主演'},
        {'id': '12', 'movie_id': '1005', 'actor_id': '2010', 'relation_type': '主演'},
        {'id': '13', 'movie_id': '1006', 'actor_id': '2011', 'relation_type': '导演'},
        {'id': '14', 'movie_id': '1006', 'actor_id': '2012', 'relation_type': '主演'},
        {'id': '15', 'movie_id': '1006', 'actor_id': '2013', 'relation_type': '主演'},
        {'id': '16', 'movie_id': '1007', 'actor_id': '2014', 'relation_type': '导演'},
        {'id': '17', 'movie_id': '1007', 'actor_id': '2015', 'relation_type': '主演'},
        {'id': '18', 'movie_id': '1008', 'actor_id': '2016', 'relation_type': '导演'},
        {'id': '19', 'movie_id': '1008', 'actor_id': '2017', 'relation_type': '主演'},
        {'id': '20', 'movie_id': '1009', 'actor_id': '2018', 'relation_type': '导演'},
        {'id': '21', 'movie_id': '1009', 'actor_id': '2019', 'relation_type': '主演'},
        {'id': '22', 'movie_id': '1009', 'actor_id': '2020', 'relation_type': '主演'},
        {'id': '23', 'movie_id': '1010', 'actor_id': '2021', 'relation_type': '导演'},
        {'id': '24', 'movie_id': '1010', 'actor_id': '2022', 'relation_type': '主演'},
        {'id': '25', 'movie_id': '1011', 'actor_id': '2023', 'relation_type': '导演'},
        {'id': '26', 'movie_id': '1011', 'actor_id': '2006', 'relation_type': '主演'},
        {'id': '27', 'movie_id': '1011', 'actor_id': '2024', 'relation_type': '主演'},
        {'id': '28', 'movie_id': '1012', 'actor_id': '2025', 'relation_type': '导演'},
        {'id': '29', 'movie_id': '1012', 'actor_id': '2026', 'relation_type': '主演'},
        {'id': '30', 'movie_id': '1012', 'actor_id': '2027', 'relation_type': '主演'},
        {'id': '31', 'movie_id': '1012', 'actor_id': '2028', 'relation_type': '主演'},
        {'id': '32', 'movie_id': '1013', 'actor_id': '2029', 'relation_type': '导演'},
        {'id': '33', 'movie_id': '1013', 'actor_id': '2030', 'relation_type': '主演'},
        {'id': '34', 'movie_id': '1013', 'actor_id': '2009', 'relation_type': '主演'},
        {'id': '35', 'movie_id': '1013', 'actor_id': '2031', 'relation_type': '主演'},
        {'id': '36', 'movie_id': '1015', 'actor_id': '2032', 'relation_type': '导演'},
        {'id': '37', 'movie_id': '1015', 'actor_id': '2015', 'relation_type': '导演'},
        {'id': '38', 'movie_id': '1015', 'actor_id': '2011', 'relation_type': '导演'},
        {'id': '39', 'movie_id': '1015', 'actor_id': '2015', 'relation_type': '主演'},
        {'id': '40', 'movie_id': '1015', 'actor_id': '2033', 'relation_type': '主演'},
        {'id': '41', 'movie_id': '1015', 'actor_id': '2034', 'relation_type': '主演'},
        {'id': '42', 'movie_id': '1016', 'actor_id': '2035', 'relation_type': '导演'},
        {'id': '43', 'movie_id': '1016', 'actor_id': '2035', 'relation_type': '主演'},
        {'id': '44', 'movie_id': '1016', 'actor_id': '2036', 'relation_type': '主演'},
        {'id': '45', 'movie_id': '1016', 'actor_id': '2022', 'relation_type': '主演'},
        {'id': '46', 'movie_id': '1017', 'actor_id': '2037', 'relation_type': '导演'},
        {'id': '47', 'movie_id': '1017', 'actor_id': '2038', 'relation_type': '导演'},
        {'id': '48', 'movie_id': '1017', 'actor_id': '2008', 'relation_type': '导演'},
        {'id': '49', 'movie_id': '1017', 'actor_id': '2001', 'relation_type': '主演'},
        {'id': '50', 'movie_id': '1017', 'actor_id': '2039', 'relation_type': '主演'},
        {'id': '51', 'movie_id': '1018', 'actor_id': '2040', 'relation_type': '导演'},
        {'id': '52', 'movie_id': '1018', 'actor_id': '2019', 'relation_type': '主演'},
        {'id': '53', 'movie_id': '1018', 'actor_id': '2041', 'relation_type': '主演'}
    ]

   # 电影信息数据添加
    for movie in movies_data:
      movie_instance = MovieInfo(
        movie_id=movie['movie_id'],
        movie_name=movie['movie_name'],
        release_date=datetime.strptime(movie['release_date'], '%Y-%m-%d'),
        country=movie['country'],
        genre=movie['genre'],
        year=movie['year']
      )
      db.session.add(movie_instance)

# 票房信息数据添加
    for box_office in box_office_data:
      box_office_instance = MoveBox(
        movie_id=box_office['movie_id'],
        box=box_office['box']
      )
      db.session.add(box_office_instance)

# 演员信息数据添加
    for actor in actors_data:
      actor_instance = ActorInfo(
        actor_id=actor['actor_id'],
        actor_name=actor['actor_name'],
        gender=actor['gender'],
        country=actor['country']
      )
      db.session.add(actor_instance)

# 电影和演员关系数据添加
    for relation in movie_actor_relations:
      relation_instance = MovieActorRelation(
        id=relation['id'],
        movie_id=relation['movie_id'],
        actor_id=relation['actor_id'],
        relation_type=relation['relation_type']
      )
      db.session.add(relation_instance)

    db.session.commit()
    print("Database populated with all data.")
    
@app.route('/')
def index():
    return render_template('index.html')
    movies = MovieInfo.query.all()  # 获取所有电影


@app.route('/search_movies', methods=['GET', 'POST'])
def search_movies():
    movie_results = []
    if request.method == 'POST':
        movie_query = request.form.get('movie_search')
        if movie_query:
            movies = MovieInfo.query.filter(MovieInfo.movie_name.ilike(f'%{movie_query}%')).all()
            for movie in movies:
                actors = ActorInfo.query.join(MovieActorRelation, ActorInfo.actor_id == MovieActorRelation.actor_id)\
                                        .filter(MovieActorRelation.movie_id == movie.movie_id, MovieActorRelation.relation_type == '主演').all()
                directors = ActorInfo.query.join(MovieActorRelation, ActorInfo.actor_id == MovieActorRelation.actor_id)\
                                           .filter(MovieActorRelation.movie_id == movie.movie_id, MovieActorRelation.relation_type == '导演').all()
                box_office = MoveBox.query.filter_by(movie_id=movie.movie_id).first()
                box_office_value = box_office.box if box_office else '无数据'
                movie_results.append({
                    'name': movie.movie_name,
                    'year': movie.year,
                    'release_date': movie.release_date.strftime('%Y-%m-%d'),
                    'country': movie.country,
                    'genre': movie.genre,
                    'directors': [director.actor_name for director in directors],
                    'box_office': box_office_value,
                    'actors': [actor.actor_name for actor in actors]
                })

    return render_template('search_movies.html', movies=movie_results)



@app.route('/search_actors', methods=['GET', 'POST'])
def search_actors():
    actor_results = []
    if request.method == 'POST':
        actor_query = request.form.get('actor_search')
        if actor_query:
            actors = ActorInfo.query.filter(ActorInfo.actor_name.ilike(f'%{actor_query}%')).all()
            for actor in actors:
                movies_as_actor = MovieInfo.query.join(MovieActorRelation, MovieInfo.movie_id == MovieActorRelation.movie_id)\
                                                 .filter(MovieActorRelation.actor_id == actor.actor_id, MovieActorRelation.relation_type == '主演').all()
                movies_as_director = MovieInfo.query.join(MovieActorRelation, MovieInfo.movie_id == MovieActorRelation.movie_id)\
                                                    .filter(MovieActorRelation.actor_id == actor.actor_id, MovieActorRelation.relation_type == '导演').all()
                actor_results.append({
                    'name': actor.actor_name,
                    'country': actor.country,
                    'movies_as_actor': [{'name': movie.movie_name, 'year': movie.year} for movie in movies_as_actor],
                    'movies_as_director': [{'name': movie.movie_name, 'year': movie.year} for movie in movies_as_director]
                })

    return render_template('search_actors.html', actors=actor_results)



@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        # 获取电影信息并创建电影实例
        new_movie_name = request.form.get('movie_name')
        new_movie_year = request.form.get('movie_year')
        new_movie_release_date = request.form.get('release_date')
        new_movie_country = request.form.get('country')
        new_movie_genre = request.form.get('genre')

        # 确保获取了所有必要的信息
        if not all([new_movie_name, new_movie_year, new_movie_release_date, new_movie_country, new_movie_genre]):
            # 如果有任何一个信息缺失，可以在这里处理错误
            return "缺少必要的电影信息", 400

        new_movie = MovieInfo(
            movie_name=new_movie_name,
            year=int(new_movie_year),
            release_date=datetime.strptime(new_movie_release_date, '%Y-%m-%d'),
            country=new_movie_country,
            genre=new_movie_genre
        )
        db.session.add(new_movie)
        db.session.flush()  # 立即生成新电影的ID

        # 添加票房信息
        new_movie_box_office = request.form.get('box_office')
        if new_movie_box_office:
            existing_box_office = MoveBox.query.filter_by(movie_id=new_movie.movie_id).first()
            if existing_box_office:
                existing_box_office.box = float(new_movie_box_office)
            else:
                new_box_office = MoveBox(
                    movie_id=new_movie.movie_id,
                    box=float(new_movie_box_office)
                )
                db.session.add(new_box_office)

        # 处理多个新演员
        new_actor_names = request.form.getlist('new_actor_name[]')
        new_actor_genders = request.form.getlist('new_actor_gender[]')
        new_actor_countries = request.form.getlist('new_actor_country[]')
        for name, gender, country in zip(new_actor_names, new_actor_genders, new_actor_countries):
            if name:
                existing_actor = ActorInfo.query.filter_by(actor_name=name).first()
                if existing_actor:
                    # 如果演员已存在，更新信息
                    existing_actor.gender = gender
                    existing_actor.country = country
                    db.session.flush()
                    new_actor_relation = MovieActorRelation(
                        movie_id=new_movie.movie_id,
                        actor_id=existing_actor.actor_id,
                        relation_type='主演'
                    )
                else:
                    # 如果演员不存在，创建新演员
                    new_actor = ActorInfo(actor_name=name, gender=gender, country=country)
                    db.session.add(new_actor)
                    db.session.flush()
                    new_actor_relation = MovieActorRelation(
                        movie_id=new_movie.movie_id,
                        actor_id=new_actor.actor_id,
                        relation_type='主演'
                    )

                db.session.add(new_actor_relation)

        # 处理多个新导演
        new_director_names = request.form.getlist('new_director_name[]')
        new_director_genders = request.form.getlist('new_director_gender[]')
        new_director_countries = request.form.getlist('new_director_country[]')
        for name, gender, country in zip(new_director_names, new_director_genders, new_director_countries):
            if name:
                existing_director = ActorInfo.query.filter_by(actor_name=name).first()
                if existing_director:
                    # 如果导演已存在，更新信息
                    existing_director.gender = gender
                    existing_director.country = country
                    db.session.flush()
                    new_director_relation = MovieActorRelation(
                        movie_id=new_movie.movie_id,
                        actor_id=existing_director.actor_id,
                        relation_type='导演'
                    )
                else:
                    # 如果导演不存在，创建新导演
                    new_director = ActorInfo(actor_name=name, gender=gender, country=country)
                    db.session.add(new_director)
                    db.session.flush()
                    new_director_relation = MovieActorRelation(
                        movie_id=new_movie.movie_id,
                        actor_id=new_director.actor_id,
                        relation_type='导演'
                    )

                db.session.add(new_director_relation)

        db.session.commit()
        return redirect(url_for('index'))

    actors = ActorInfo.query.all()
    return render_template('add_movie.html', actors=actors)



@app.route('/movie_list')
def movie_list():
    movies = MovieInfo.query.all()
    return render_template('movie_list.html', movies=movies)


@app.route('/movie/<int:movie_id>')
def show_movie(movie_id):
    movie = MovieInfo.query.get_or_404(movie_id)
    box_office = MoveBox.query.filter_by(movie_id=movie_id).first()

    # 获取电影的演员信息
    actors = ActorInfo.query.join(MovieActorRelation, ActorInfo.actor_id == MovieActorRelation.actor_id)\
                            .filter(MovieActorRelation.movie_id == movie.movie_id, MovieActorRelation.relation_type == '主演').all()

    # 获取电影的导演信息
    directors = ActorInfo.query.join(MovieActorRelation, ActorInfo.actor_id == MovieActorRelation.actor_id)\
                               .filter(MovieActorRelation.movie_id == movie.movie_id, MovieActorRelation.relation_type == '导演').all()

    return render_template('show_movie.html', movie=movie, box_office=box_office, actors=actors, directors=directors)



@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    # 获取电影实例
    movie = MovieInfo.query.get_or_404(movie_id)

    # 删除与电影相关的演员和导演关系
    MovieActorRelation.query.filter_by(movie_id=movie.movie_id).delete()

    # 删除电影的票房信息
    MoveBox.query.filter_by(movie_id=movie.movie_id).delete()

    # 删除电影本身
    db.session.delete(movie)

    # 提交更改
    db.session.commit()

    flash('电影及相关信息已删除')
    return redirect(url_for('index'))



@app.route('/box_office_analysis')
def box_office_analysis():
    # 获取票房前十的电影
    top_movies_analysis = db.session.query(
        MovieInfo.movie_name, func.sum(MoveBox.box)
    ).join(MoveBox).group_by(MovieInfo.movie_name).order_by(func.sum(MoveBox.box).desc()).limit(10).all()

    # 按类型分析票房
    genre_analysis = db.session.query(
        MovieInfo.genre, func.sum(MoveBox.box)
    ).join(MoveBox).group_by(MovieInfo.genre).all()

    # 按国家分析票房
    country_analysis = db.session.query(
        MovieInfo.country, func.sum(MoveBox.box)
    ).join(MoveBox).group_by(MovieInfo.country).all()

    # 按年份分析票房
    year_analysis = db.session.query(
        MovieInfo.year, func.sum(MoveBox.box)
    ).join(MoveBox).group_by(MovieInfo.year).all()
    
    
    # 按电影分析票房
    movie_box_office_analysis = db.session.query(
        MovieInfo.movie_name, func.sum(MoveBox.box)
    ).join(MoveBox).group_by(MovieInfo.movie_name).all()


    # 数据转换为前端格式
    top_movie_names, top_movie_box_offices = zip(*top_movies_analysis)
    genres, genre_box_offices = zip(*genre_analysis)
    countries, country_box_offices = zip(*country_analysis)
    years, year_box_offices = zip(*year_analysis)
    movie_names, movie_box_offices = zip(*movie_box_office_analysis)


    return render_template(
        'box_office_analysis.html',
        genres=list(genres),
        genre_box_offices=list(genre_box_offices),
        countries=list(countries),
        country_box_offices=list(country_box_offices),
        years=list(years),
        year_box_offices=list(year_box_offices),
        movie_names=list(movie_names),
        movie_box_offices=list(movie_box_offices),
        top_movie_names=list(top_movie_names),
        top_movie_box_offices=list(top_movie_box_offices),
    )



# Route to display a list of actors
@app.route('/actor_list')
def actor_list():
    actors = ActorInfo.query.all()
    return render_template('actor_list.html', actors=actors)


# Route to display the details of a specific actor
@app.route('/show_actor/<int:actor_id>')
def show_actor(actor_id):
    actor = ActorInfo.query.get_or_404(actor_id)

    # 获取演员参与的电影作为主演的列表
    movies_as_actor = MovieInfo.query.join(MovieActorRelation, MovieInfo.movie_id == MovieActorRelation.movie_id)\
                                     .filter(MovieActorRelation.actor_id == actor.actor_id, MovieActorRelation.relation_type == '主演').all()

    # 获取演员参与的电影作为导演的列表
    movies_as_director = MovieInfo.query.join(MovieActorRelation, MovieInfo.movie_id == MovieActorRelation.movie_id)\
                                        .filter(MovieActorRelation.actor_id == actor.actor_id, MovieActorRelation.relation_type == '导演').all()

    return render_template('show_actor.html', actor=actor, movies_as_actor=movies_as_actor, movies_as_director=movies_as_director)

# Route to handle actor deletion
@app.route('/delete_actor/<int:actor_id>', methods=['POST'])
def delete_actor(actor_id):
    actor = ActorInfo.query.get_or_404(actor_id)

    # 删除该演员相关的所有电影演员关系
    MovieActorRelation.query.filter_by(actor_id=actor.actor_id).delete()

    db.session.delete(actor)
    db.session.commit()
    flash('演员删除成功。')
    return redirect(url_for('actor_list'))

@app.route('/box_office_list')
def box_office_list():
    # 获取电影数据并按票房从高到低排序
    movies = MovieInfo.query.join(MoveBox, MovieInfo.movie_id == MoveBox.movie_id)\
                            .order_by(MoveBox.box.desc()).all()
    return render_template('box_office_list.html', movies=movies)



@app.route('/search_by_genre', methods=['GET', 'POST'])
def search_by_genre():
    genres = db.session.query(MovieInfo.genre).distinct().all()  # 获取所有独特的电影类别
    genre_list = [genre[0] for genre in genres]  # 将类别转换为列表

    selected_genre = request.args.get('genre')  # 从请求中获取选定的类别
    if selected_genre:
        movies = MovieInfo.query.filter_by(genre=selected_genre).all()
    else:
        movies = []

    return render_template('search_by_genre.html', genres=genre_list, movies=movies, selected_genre=selected_genre)

@app.route('/search_by_year', methods=['GET', 'POST'])
def search_by_year():
    years = db.session.query(MovieInfo.year).distinct().all()  # 获取所有独特的电影年份
    year_list = [year[0] for year in years]  # 将年份转换为列表

    selected_year = request.args.get('year')  # 从请求中获取选定的年份
    if selected_year:
        selected_year_int = int(selected_year)  # 将字符串转换为整数
        movies = MovieInfo.query.filter_by(year=selected_year_int).all()
    else:
        movies = []

    return render_template('search_by_year.html', years=year_list, movies=movies, selected_year=selected_year)


if __name__ == '__main__':
    app.run(debug=True)


