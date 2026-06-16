from fastapi import FastAPI
from app.routers import users
from app.security import authentication
from .exception import EmailAlreadyExists,NoUserExists,InvalidCredentials
from fastapi.responses import JSONResponse
import logging

app = FastAPI()
app.include_router(users.router)
app.include_router(authentication.router)

logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.exception_handler(EmailAlreadyExists)
def email_exist_exception_handler(request, exc):
    return JSONResponse(status_code=409, content={'Message': 'Email already exits'})

@app.exception_handler(NoUserExists)
def no_user_exist_exception_handler(request, exc):
    return JSONResponse(status_code=404, content={'Message': 'No User Exists'})

@app.exception_handler(InvalidCredentials)
def invalid_credentials_exception_handler(request, exc):
    return JSONResponse(status_code=401, content={'Message': 'Invalid Credentials'})
