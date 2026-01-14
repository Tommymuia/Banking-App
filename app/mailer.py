from flask_mail import Mail, Message
from flask import current_app

mail = Mail()


def init_mail(app):
    """
    Connects Flask-Mail to the Flask app
    """
    mail.init_app(app)


def send_email(to_email, subject, body):
    """
    Sends a basic text email
    """
    msg = Message(
        subject=subject,
        recipients=[to_email],
        body=body,
        sender=current_app.config["MAIL_DEFAULT_SENDER"]

    )
    mail.send(msg)    