from flask import render_template
from app import apps

@apps.route('/')
@apps.route('/index')
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