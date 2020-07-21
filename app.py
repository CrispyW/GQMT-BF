import os
import sys
import io
import base64
import click

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash # 密码保护

from model import *

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# 设置app
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@login_manager.user_loader
def load_user(user_id): # 创建用户加载回调函数，接受用户ID作为参数
	user = User.query.get(int(user_id)) # 用ID作为User模型的主键查询对应的用户
	return(user) # 返回用户对象

# 命令：创建和管理admin账号
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')

# 让User类继承db.Model和UserMixin类
# UserMixin 让存储用户的 User 模型类继承 Flask-Login 提供的 UserMixin类, 继承这个类会让 User 类拥有几个用于判断认证状态的属性和方法
class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password): # 生成hash密码
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password): # 验证hash密码
        return check_password_hash(self.password_hash, password)

# web app功能
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    if not current_user.is_authenticated:
    	return redirect(url_for('login'))
    data = read_time_series()
    output = model_output(data).round(2)

    img = io.BytesIO()
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Value'])
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('homepage.html', output = output, plot_url=plot_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('无效输入')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('登陆成功')
            return redirect(url_for('home'))

        flash('账号或密码不正确')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('再见')
    return redirect(url_for('login'))
