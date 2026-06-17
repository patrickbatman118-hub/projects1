import bcrypt
from ..models import users as models_users
from ..schemas import users as schema_users


def hash_password(user: schema_users.user):
    hashed_password = bcrypt.hashpw(user.password.encode(),bcrypt.gensalt()).decode()
    user_data = user.model_dump()
    user_data['password'] = hashed_password
    user_data.pop('confirm_password')
    new_user = models_users.User(**user_data)
    return new_user