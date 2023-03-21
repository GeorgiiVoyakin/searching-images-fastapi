from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class ImageObject(BaseModel):
    image_id: int
    object: str

    class Config:
        orm_mode = True


class ImageBase(BaseModel):
    path: str


class ImageCreate(ImageBase):
    pass


class Image(ImageBase):
    id: int
    owner_id: int

    objects: list[ImageObject] = []

    class Config:
        orm_mode = True


class AlbumBase(BaseModel):
    name: str


class AlbumCreate(AlbumBase):
    pass


class Album(AlbumBase):
    id: int
    owner_id: int

    images: list[Image] = []

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
    albums: list[Album] = []
    favorites: list[Image] = []

    class Config:
        orm_mode = True


class Favorite(BaseModel):
    image_id: int
    owner_id: int

    class Config:
        orm_mode = True
