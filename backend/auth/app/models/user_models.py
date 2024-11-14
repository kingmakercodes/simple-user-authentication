from app import database
from datetime import datetime, timezone, timedelta
from app import password_hasher

# base user from which pending users and registered users will inherit from
class BaseUser(database.Model):
    __abstract__= True

    id= database.Column(database.Integer, primary_key=True)
    fullname= database.Column(database.String(40), nullable=False)
    email= database.Column(database.String(50), unique=True, nullable=False)
    created_at= database.Column(database.DateTime, default=datetime.now(timezone.utc))

# pending user model
class PendingUser(BaseUser):
    __tablename__='pending_users'

    password= database.Column(database.String(120), nullable=False)
    token= database.Column(database.String(500), nullable=False)

# registered user model
class RegisteredUser(BaseUser):
    __tablename__='users'

    password_hash= database.Column(database.String(260), nullable=False)

    # password hashing functions, using argon2
    def set_password(self, password):
        self.password_hash= password_hasher.hash(password)

    def check_password(self, password):
        try:
            return password_hasher.verify(self.password_hash, password)
        except Exception:
            return False