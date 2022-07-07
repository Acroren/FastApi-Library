from fastapi import Form, File, UploadFile
from pydantic import BaseModel


class LoginForm(BaseModel):
    username: str
    password: str
    # file: UploadFile

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
        # file: UploadFile = File(...)
    ):
        return cls(
            username=username,
            password=password,
            # file=file
        )


class BookForm(BaseModel):
    title: str
    saga: str
    sinopsis: str
    image: str

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        saga: str = Form(...),
        sinopsis: str = Form(...),
        image: str = Form(...),
    ):
        return cls(
            title=title,
            saga=saga,
            sinopsis=sinopsis,
            image=image
        )
