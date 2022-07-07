import json

from fastapi import Body, FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from schemas import LoginForm, BookForm
from enum import Enum

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class Perms(Enum):
    GUEST = 0,
    USER = 1,
    ADMIN = 2


class User(BaseModel):
    username: str
    password: str


class Book(BaseModel):
    name: str
    saga: str | None = None
    sinopsis: str
    price: float = Field(gt=0, description="The price must be greater than zero")
    pages: int = Field(gt=0, description="The pages must be greater than zero")
    url: str


@app.on_event('startup')
def startup():
    global current_perm
    current_perm = Perms.GUEST


# Root site
# Load the HTML page with the necessary information:
# - Book list: from the database
# - User permits: Guest, User, Admin
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    print("Welcome " + current_perm.name)
    # Loads the books from de DB
    with open("db/books.json") as f:
        data_books = json.load(f)
    book_list = data_books["books"]

    # Load the HTML page
    return templates.TemplateResponse("index.html", {
        "request": request,
        "book_list": book_list,
        "perm": current_perm,
    })


# *** Login site ***
# Load the html form
@app.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "perm": current_perm,
    })


# Manage the login options:
# - If login success --> Go to Index with the perms:
#       - If the username credentials are the same as the admin --> Admin
#       - Else --> User
# - Else, If login not success --> Return to Login page
@app.post("/login/")
async def login(request: Request, form_data: LoginForm = Depends(LoginForm.as_form)):
    # Load the list of all users
    with open("db/users.json") as f:
        data = json.load(f)
    global current_perm
    # ** Check validations **
    # If the username are the same as the admin username, check password
    if form_data.username == str(data['admin']['username']):
        if form_data.password == str(data['admin']['password']):
            # Go to the root as an admin
            current_perm = Perms.ADMIN
            resp = RedirectResponse("/")
            resp.status_code = 302
        # Return to login
        else:
            print("FALLO")
            resp = RedirectResponse("/login")
            resp.status_code = 302
        return resp

    # Else check if the username exist and the passowrd is correct
    else:
        for i in data["users"]:
            if form_data.username  == str(i['username']) and form_data.password == str(i['password']):
                # Go to the root as an user
                current_perm = Perms.USER
                resp = RedirectResponse("/")
                resp.status_code = 302
                return resp
        # Else return to login
        print("FALLO")
        resp = RedirectResponse("/login")
        resp.status_code = 302
        return resp


# *** Add site ***
# Load the html form
@app.get("/add/", response_class=HTMLResponse)
async def add(request: Request):
    return templates.TemplateResponse("add_book.html", {
        "request": request,
        "perm": current_perm,
    })


# Save the new book in the BD
# Falta comprobar integridad
@app.post("/add/", response_class=HTMLResponse)
async def add(request: Request, form_data: BookForm = Depends(BookForm.as_form)):
    # 1. Read file contents
    with open("db/books.json") as file:
        data = json.load(file)

    # 2. Update json object
    new_id = int(data["books"][len(data["books"])-1]["id"])+1
    entry = {"id": str(new_id),
             "name": form_data.title,
             "saga": form_data.saga,
             "sinopsis": form_data.sinopsis,
             "price": "17",
             "pages": "500",
             "url": form_data.image}
    data['books'].append(entry)

    # 3. Write json file
    with open("db/books.json", "w") as file:
        json.dump(data, file)
    resp = RedirectResponse("/")
    resp.status_code = 302
    return resp


# Show the selected book
@app.get("/book/{book_id}", response_class=HTMLResponse)
async def home(request: Request, book_id: int):
    with open("db/books.json") as f:
        data_books = json.load(f)
        for i in data_books ["books"]:
            if int(i["id"]) == book_id:
                book = i
    # Load the HTML page
    return templates.TemplateResponse("book.html", {
        "request": request,
        "book": book,
        "perm": current_perm,
    })


# PENDIENTE, ANTES DE BORRAR, REVISAR SI EL USU ES ADMIN
@app.get("/remove/{book_id}", response_class=HTMLResponse)
async def home(request: Request, book_id: str):
    with open("db/books.json") as f:
        data_books = json.load(f)
        position = -1
        for i in range(len(data_books["books"])):
            print(data_books["books"][i]["id"])
            if data_books["books"][i]["id"] == book_id:
                position = i
                print("found" + str(i))
                break
        if position != -1:
            data_books["books"].pop(position)
        with open("db/books.json", "w") as f:
            json.dump(data_books, f)

    # Load the HTML page
    resp = RedirectResponse("/")
    resp.status_code = 302
    return resp
