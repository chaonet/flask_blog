# -*- coding:utf-8 -*-
from flask import render_template, flash, redirect
from app import app
from .forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Miguel'}
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
             'author': {'nickname': 'Susan'},
             'body': 'The Avengers movie was so cool'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts = posts)
    # return "Hello, World!"

# print __name__,3 # app.views
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm() # 实例化
    # print dir(form)
    '''
['Meta', 'SECRET_KEY', 'TIME_LIMIT', '__class__', '__contains__', '__delattr__', '__delitem__', '__dict__', '__doc__', '__format__', '__getattribute__', '__getitem__', '__hash__', '__init__', '__iter__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_errors', '_fields', '_get_translations', '_prefix', '_unbound_fields', '_wtforms_meta', 'csrf_enabled', 'csrf_token', 'data', 'errors', 'generate_csrf_token', 'hidden_tag', 'is_submitted', 'meta', 'openid', 'populate_obj', 'process', 'remember_me', 'validate', 'validate_csrf_data', 'validate_csrf_token', 'validate_on_submit']
    '''
    if form.validate_on_submit():
        # print 'yes'
        flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
        return redirect('/index')
    # print 'no'
    return render_template('login.html', title='Sing In', form=form)