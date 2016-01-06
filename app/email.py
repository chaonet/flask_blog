import config
from flask import render_template, current_app
from flask.ext.mail import Message
from . import mail

def send_email(to, subject, template, **kwargs):
    # print dir(current_app.config)
    msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)