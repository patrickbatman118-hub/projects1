from fastapi import FastAPI
from routers import users,authentication
from .exception import EmailAlreadyExists
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


