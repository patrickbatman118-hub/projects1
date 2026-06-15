from fastapi import FastAPI
from routers import users
from .exception import EmailAlreadyExists
from fastapi.responses import JSONResponse
import logging

app = FastAPI()
app.include_router(users.router)

logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.exception_handler(EmailAlreadyExists)
def email_exist_exception_handler(request, exc):
    JSONResponse(Status_code=400, content={'Message': 'Email already exits'})


