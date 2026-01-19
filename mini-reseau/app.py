#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, flash, session, g
import pymysql.cursors

app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'

######################CONNECTION################################

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host="localhost",  # à modifier
            user="valou",  # à modifier
            password="1301",  # à modifier
            database="noel",  # à modifier
            charset='utf8mb4',
            port=3307,
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

###########################################################

@app.route('/')
def show_layout():
    return render_template('layout.html')


if __name__ == '__main__':
    app.run(debug=True)
