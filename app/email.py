import config
from flask import render_template
from flask.ext.mail import Message
from . import mail

def send_email(to, subject, template, **kwargs):
    msg = Message(subject, sender=config.MAIL_USERNAME, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)