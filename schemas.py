from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class ImageBase(BaseModel):
    path: str
    objects_list: list[str]


class ImageCreate(ImageBase):
    pass


class Image(ImageBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str

    def __str__(self) -> str:
        return f"username: {self.username}, email: {self.email}"


class UserCreate(UserBase):
    password: str

    def __str__(self) -> str:
        return super().__str__()


class User(UserBase):
    is_active: bool

    images: list[Image] = []

    class Config:
        orm_mode = True
