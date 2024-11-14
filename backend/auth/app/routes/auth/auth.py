import os
from datetime import datetime, timezone, timedelta
import jwt
from flask import Blueprint, request, jsonify, make_response
from app.utils.auth_utils import generate_verification_token, verify_verification_token, send_confirmation_email, send_verification_email
from app import database
from app.models.user_models import PendingUser, RegisteredUser

auth_blueprint= Blueprint('auth',__name__)

# home route
@auth_blueprint.route('/', methods=['GET'])
def home():
    return f'<h1>Welcome to the homepage</h1>'

# user signup route
@auth_blueprint.route('/signup', methods=['POST'])
def signup():
    try:
        token= request.args.get('token')
        data= request.get_json()
        fullname= data.get('fullname')
        email= data.get('email')
        password= data.get('password')

        user_registered= RegisteredUser.query.filter_by(email=email).first()
        if user_registered:
            return jsonify({
                'message':'User email already registered. Please log in with this email instead.'
            })

        user_pending= PendingUser.query.filter_by(email=email).first()
        if user_pending:
            return jsonify({
                'message':'Your registration is still pending, please check your email for a verification link',
                'token': token
            }), 400

        user_pending= PendingUser(
            fullname=fullname,
            email=email,
            password=password
        )

        # generate verification token for this email
        token= generate_verification_token(email)
        user_pending.token= token

        database.session.add(user_pending)
        database.session.commit()

        # send verification email to pending user email
        send_verification_email(email, token)

        return jsonify({
            'message':'A verification email has been sent to the provided email. Please check your inbox to verify your email address.',
            'token': token
        }), 200

    except Exception as e:
        database.session.rollback()
        return jsonify({'error':f'An error occurred during registration, {e}'})


# verify email route
@auth_blueprint.route('/verify-email', methods=['GET'])
def verify_email():
    try:
        # fetch token from request
        token= request.args.get('token')
        if not token:
            return jsonify({'error':'Missing verification token!'}), 400

        # if token exists, verify token from email
        email= verify_verification_token(token)

        if not email:
            return jsonify({'error':'Invalid or expired token!'}), 400

        # if existing token is valid, check if user email already exists
        user_exists= RegisteredUser.query.filter_by(email=email).first()

        if user_exists:
            return jsonify({'message':'User email already exists! Please try again with a different email!'}), 400

        # check if the email is pending verification
        pending_user = PendingUser.query.filter_by(email=email).first()
        if not pending_user:
            return jsonify({'message': 'User not found!'}), 400

        # if token from email is valid, and email is pending verification, transfer pending user details to registered user
        new_user= RegisteredUser(
            fullname= pending_user.fullname,
            email= pending_user.email
        )
        new_user.set_password(pending_user.password)

        # commit new user to database
        database.session.add(new_user)

        # delete pending user data from database before commit
        database.session.delete(pending_user)
        database.session.commit()

        # send verified email confirmation email to user email
        send_confirmation_email(email)

        return jsonify({'message':'New user created successfully!'}), 201

    except Exception as e:
        # clear database of saved data
        database.session.rollback()
        return jsonify({'error':f'An error occurred while verifying email, {e}'}), 500


# user login route
@auth_blueprint.route('/login', methods=['POST'])
def login():
    try:
        # collect client-validated user login details, empty fields to be handled client-side
        data= request.get_json()
        email= data.get('email')
        password= data.get('password')

        # fetch user attributes
        user= RegisteredUser.query.filter_by(email=email, password_hash=password).first()
        if not user:
            return jsonify({'message':'User does not exist!'}), 404

        # if user exists, check password against databased password
        valid_password= user.check_password(user.password_hash, password)
        if not valid_password:
            return jsonify({'error':'Invalid password'}), 401

        # if password match, generate token for user login session specific to user id
        payload = {
            'user_id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=3)
        }
        jwt_secret_key = os.getenv('JWT_SECRET_KEY')
        token = jwt.encode(payload, jwt_secret_key, algorithm='HS256')

        # create response and set the cookies
        response= make_response(jsonify({
            'message':'User logged in successfully!',
            'token':token
        }))
        response.set_cookie(
            'token',
            token,
            httponly=True,
            secure=True,
            samesite='Strict'
        )

        return response, 200

    except Exception as e:
        return jsonify({'error':f'An internal error occurred while trying to log in, {e}'}), 500