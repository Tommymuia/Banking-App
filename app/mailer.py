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

    def send_transaction_alert(to_email, amount, transaction_type):
    """
    Sends a banking transaction alert email
    """
    subject = "Transaction Alert"


    body = (
        f"Dear Customer,\n\n"
        f"A {transaction_type} of ${amount} has occurred on your account.\n\n"
        f"If this was not you, please contact support immediately.\n\n"
        f"- Your Bank, thank you for banking with us."
    )
    send_email(to_email, subject, body)