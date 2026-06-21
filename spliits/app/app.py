from fastapi import FastAPI, HTTPException
from app.routers import users, pools, requests
from app.security import authentication
from .exception import EmailAlreadyExists,NoUserExists,InvalidCredentials,NoPoolExist,AlreadyInThePool
from fastapi.responses import JSONResponse
import logging

app = FastAPI()
app.include_router(users.router)
app.include_router(authentication.router)
app.include_router(pools.router)
app.include_router(requests.router)


logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)


logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



@app.exception_handler(EmailAlreadyExists)
def email_exist_exception_handler(request, exc):
    return JSONResponse(status_code=409, content={'Message': 'Email already exits'})

@app.exception_handler(NoUserExists)
def no_user_exist_exception_handler(request, exc):
    return JSONResponse(status_code=404, content={'Message': 'No User Exists'})

@app.exception_handler(InvalidCredentials)
def invalid_credentials_exception_handler(request, exc):
    return JSONResponse(status_code=401, content={'Message': 'Invalid Credentials'})

@app.exception_handler(NoPoolExist)
def No_Pool_Found(request, exc):
    return JSONResponse(status_code=404, content={'Message': 'No Pool Found'})

@app.exception_handler(AlreadyInThePool)
def already_in_pool_exception_handler(request, exc):
    return JSONResponse(status_code=409, content={'Message': 'Already in the pool'})


