from flask import url_for
from flask_mail import Message
from . import mail

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('account.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def notify(user):
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''An account has been created for you with the default password as 'password'. Please login and change your password through the following link:
{url_for('auth.login', _external=True)}
'''
    mail.send(msg)

def approve(user,vehicleno):
   msg = Message('Appeal Status', sender = 'noreply@demo.com', recipients = [user.email])
   msg.body = "This is to inform you that your appeal request for Vehicle No:"+ vehicleno + " has been approved."
   mail.send(msg)


def reject(user,vehicleno):
   msg = Message('Appeal Status', sender = 'noreply@demo.com', recipients = [user.email])
   msg.body = "This is to inform you that your appeal request for Vehicle No:"+ vehicleno + " has been rejected."
   mail.send(msg)

def blacklistemail(user,vehicleno):
   msg = Message('Blacklisted Vehicle', sender = 'noreply@demo.com', recipients = 'acrsfyproject@gmail.com')
   msg.body = "This is to inform you that Vehicle No:"+ vehicleno + " has been blacklisted."
   mail.send(msg)


