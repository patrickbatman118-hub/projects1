import bcrypt
from app import schemas, models


def hash_password(user: schemas.user):
    hashed_password = bcrypt.hashpw(user.password.encode(),bcrypt.gensalt()).decode()
    user_data = user.model_dump()
    user_data['password'] = hashed_password
    user_data.pop('confirm_password')
    new_user = models.User(**user_data)
    return new_user