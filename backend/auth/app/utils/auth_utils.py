from datetime import datetime, timezone, timedelta
from flask_mail import Message
from app import mail
import jwt
import os


# generate verification token for email
def generate_verification_token(email):
    try:
        if not email:
            raise ValueError('Email cannot be None')

        payload= {
            'email':email,
            'exp': datetime.now(timezone.utc)+ timedelta(hours=1)
        }

        jwt_secret_key= os.getenv('JWT_SECRET_KEY')
        token= jwt.encode(payload, jwt_secret_key, algorithm='HS256')

        return token

    except Exception as e:
        return f'error: An error occurred while generating token, {e}'


# verify verification token from email if matches payload
def verify_verification_token(token):
    try:
        # decode the payload
        jwt_secret_key= os.getenv('JWT_SECRET_KEY')
        payload= jwt.decode(token, jwt_secret_key, algorithms='HS256')

        email= payload.get('email')
        exp= payload.get('exp')

        if not email or not exp:
            return 'Invalid token payload!'

        # check if token is expired
        token_expiry_date= datetime.fromtimestamp(exp, tz=timezone.utc)

        if datetime.now(timezone.utc) > token_expiry_date:
            return 'Token has expired!'

        # return the email from the token payload if token is still valid
        return email

    except jwt.ExpiredSignatureError:
        return 'Token has expired!'
    except jwt.InvalidTokenError:
        return 'Invalid token!'
    except Exception as e:
        return f'Error decoding token: {str(e)}'


# send a verification email to user email, using flask-mail
def send_verification_email(email, token):
    base_url= os.getenv('BASE_URL')
    sender= os.getenv('MAIL_DEFAULT_SENDER')

    verification_link= f'{base_url}/verify-email?token={token}'
    msg= Message(
        subject='Email Verification',
        recipients=[email],
        sender=sender
    )
    msg.body= (
        'This is a send only email, please do not reply this email.\n'
        'If you have any concerns, please contact customer support.'
        '\n\n'
        'Please click on this link to verify your email:'
        f'{verification_link}'
    )

    try:
        # send email
        mail.send(msg)
        return 'Verification email sent successfully!'

    except Exception as e:
        # handle errors here
        return f'Failed to send email: {e}'


# send verification email confirmation mail to user email
def send_confirmation_email(email):
    sender= os.getenv('MAIL_DEFAULT_SENDER')
    msg= Message(
        subject='Email Verification Successful',
        recipients=[email],
        sender=sender
    )
    msg.body = (
        'Congratulations! Your email has been successfully verified.\n\n'
        'You can now fully access your account and all its features.\n\n'
        '\n\n'
        'This is a send only email, please do not reply to this email.\n'
        'If you have any concerns, please contact customer support.'
    )

    try:
        # send email
        mail.send(msg)
        return 'Confirmation email sent successfully!'
    except Exception as e:
        # handle errors here
        return f'Failed to send confirmation email: {e}'