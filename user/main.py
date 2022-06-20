import jwt

from pydantic import BaseModel

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND

from models import DBSession, User
from config import settings

app = FastAPI()

templates = Jinja2Templates(directory="templates")


class UserItem(BaseModel):
    name: str
    password: str


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    jwt_encode = request.cookies.get("jwt")
    try:
        user_json = jwt.decode(
            jwt_encode, settings.secret, algorithms=["HS256"]
        )
        user: UserItem = UserItem.parse_obj(user_json)
    except Exception as e:
        print((e))
        return RedirectResponse(url='/login')
    return templates.TemplateResponse("index.html", {"request": request, "name": user.name})


@app.get('/register/', response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post('/register/', response_class=HTMLResponse)
def register_post(name: str = Form(), password: str = Form()):
    userItem = UserItem(name=name, password=password)
    # TODO: handel error
    with DBSession() as session:
        session.add(User(
            name=userItem.name,
            password=jwt.encode(
                userItem.dict(), settings.secret, algorithm="HS256"
            )
        ))
        session.commit()
    return RedirectResponse(url='/login')


@app.get('/login/', response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post('/login/', response_class=HTMLResponse)
def login_post(name: str = Form(), password: str = Form()):
    userItem: UserItem = UserItem(name=name, password=password)
    # TODO: handel error
    with DBSession() as session:
        user = session.query(User).filter(
            User.name == userItem.name
        ).one_or_none()
        if not user:
            return f"unregister user {userItem.name}"
        jwt_encode = jwt.encode(
            userItem.dict(), settings.secret, algorithm="HS256")
        if user.password != jwt_encode:
            return "name or password is not correct"
        response = RedirectResponse(url='/', status_code=HTTP_302_FOUND)
        response.set_cookie(key="jwt", value=jwt_encode)
        return response
