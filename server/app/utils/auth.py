import random
from flask_mail import Message
from flask import current_app
import os

def generate_otp():
    return str(random.randint(100000, 999999))

def send_verification_email(to_email, otp):
    mail = current_app.extensions['mail']
    msg = Message(
        subject='Verify your email for Public Pulse',
        sender=os.getenv('EMAIL_USER'),
        recipients=[to_email],
        body=f"Thanks for registering with Public Pulse! Your OTP is: {otp}"
    )
    mail.send(msg) 