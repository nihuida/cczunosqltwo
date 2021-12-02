from flask import Flask, render_template, request, url_for
import pandas as pd
import random
from flask import Flask
from flask import Response, json, jsonify
from flask import request
from flask import render_template
from flask import flash, redirect
import mysql.connector as mysql
import mysql.connector as mysql
from flask import request
import os
import re
import suanfa
import jieba
import random


info_randomlist = []
random_num_lists = []
all_music_id_lists = []
app = Flask(__name__)
# 用户信息
db = mysql.connect(
    host="localhost",
    user="root",
    passwd="123",
    database="userdb",
    buffered=True,
    auth_plugin='mysql_native_password'
)
cursor = db.cursor()

# cursor.execute("DROP TABLE IF EXISTS USERINFO")
sql = """CREATE TABLE IF NOT EXISTS USERINFO (
         USER_ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
         USER_NAME VARCHAR(20) NOT NULL UNIQUE,
         USER_PASSWORD VARCHAR(20) NOT NULL)"""
cursor.execute(sql)
sql = """CREATE TABLE IF NOT EXISTS USERACTS (
             USER_ID INT(3) NOT NULL,
             USER_BRO_HIS_ID INT(3) NOT NULL)"""
cursor.execute(sql)
# 密钥，安全方面的考虑，本地开发可以随便设置
app.secret_key = 'secret_key'
# cursor.execute("SELECT ID FROM MUSIC_INFO")
# all_music_id_lists = cursor.fetchall()
info = suanfa.get_music_info_latest(1, cursor)
info_randomlist_main = suanfa.info_ramdom(
    info_randomlist, cursor, random_num_lists)


@app.route('/', methods=['GET', 'POST'])
def login():
    info = suanfa.get_music_info_latest(1, cursor)
    info_randomlist_main = suanfa.info_ramdom(
        info_randomlist, cursor, random_num_lists)

    if request.method == 'POST':
        username = request.form.get('u')
        password = request.form.get('p')
        print("---------- login -----------")
        print("username : ", username)
        print("password : ", password)
        if not all([username, password]):
            flash('参数不完整')
            return render_template('login.html')

        # 判断用户信息是否存在？是否正确
        cursor.execute("SELECT USER_ID,USER_NAME,USER_PASSWORD FROM USERINFO")
        results = cursor.fetchall()
        for result in results:
            username = request.form.get('u')
            password = request.form.get('p')
            if username == result[1] and password == result[2]:
                print('登录成功')
                global current_userid
                current_userid = result[0]
                # print("+++++++++++++++")
                # print("current id =", current_userid)

                mstr = str(username)
                print("uername=", username)
                return redirect(url_for('index', item0=info_randomlist_main[0],
                                        item1=info_randomlist_main[1],
                                        item2=info_randomlist_main[2],
                                        item3=info_randomlist_main[3],
                                        item4=info_randomlist_main[4],
                                        item5=info_randomlist_main[5],
                                        item6=info_randomlist_main[6],
                                        item7=info_randomlist_main[7],
                                        item8=info_randomlist_main[8],
                                        music1=info_randomlist_main[0],
                                        music2=info_randomlist_main[1],
                                        music3=info_randomlist_main[2],
                                        music4=info_randomlist_main[3],
                                        music5=info_randomlist_main[4],
                                        my_str=mstr))

    return render_template('login.html')


@app.route('/index/')
def index():
    info = suanfa.get_music_info_latest(1, cursor)
    info_randomlist_main = suanfa.info_ramdom(
        info_randomlist, cursor, random_num_lists)
    print("++++++++++++++++++++++++++++++++++")
    print("主页")
    personal_music_recomlists = suanfa.personal_music_recommend(
        cursor, current_userid, random_num_lists)
    # print("personal_music_recom =", personal_music_recomlists)
    username = request.form.get('u')
    mstr = username
    # print("uername=", username)
    return render_template('index.html', my_str=mstr,
                           item0=info_randomlist_main[0],
                           item1=info_randomlist_main[1],
                           item2=info_randomlist_main[2],
                           item3=info_randomlist_main[3],
                           item4=info_randomlist_main[4],
                           item5=info_randomlist_main[5],
                           item6=info_randomlist_main[6],
                           item7=info_randomlist_main[7],
                           item8=info_randomlist_main[8],
                           music1=personal_music_recomlists[0],
                           music2=personal_music_recomlists[1],
                           music3=personal_music_recomlists[2],
                           music4=personal_music_recomlists[3],
                           music5=personal_music_recomlists[4]
                           )


@app.route('/register/', methods=['GET', 'POST'])
def register():
    print("request.method : ", request.method)
    if request.method == 'POST':
        username = request.form.get('u')
        password = request.form.get('p')
        password2 = request.form.get('p')
        # 校验
        if not all([username, password, password2]):
            flash('参数不完整')
        elif password != password2:
            flash('两次密码不一致，请重新输入')
        else:
            # 保存用户注册信息
            cursor.execute("SELECT USER_NAME FROM USERINFO")
            global results
            results = cursor.fetchall()
            for row in results:
                if username == row[0]:
                    flash('用户名重复')
                    return render_template('register.html')
            sql = """INSERT INTO USERINFO(USER_ID,USER_NAME, USER_PASSWORD)
                    VALUES (NULL, %s, %s)""" % (username, password)
            try:
                # 执行sql语句
                cursor.execute(sql)
                # 提交到数据库执行
                db.commit()
            except:
                # 如果发生错误则回滚
                db.rollback()
            cursor.execute("SELECT * FROM USERINFO")
            result = cursor.fetchone()
            # user_info_dict[username] = password
            print("user_info_dict")
            print(result)
    return render_template('register.html')
