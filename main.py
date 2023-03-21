import io
from datetime import datetime, timedelta
from typing import List

import numpy as np
import tensorflow as tf
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from PIL import Image
from schemas import Token, TokenData, User
import crud
from utils import verify_password
import crud
import models
import schemas
from database import SessionLocal, engine
from sqlalchemy.orm import Session


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(db, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


model = tf.keras.applications.MobileNetV2()

# Преобразуем изображение в формат, который можно использовать в модели


def read_imagefile(file) -> np.ndarray:
    image = Image.open(io.BytesIO(file))
    image = image.convert('RGB')
    image = image.resize((224, 224))
    return np.array(image) / 255.0


def get_objects_on_image(image: np.ndarray) -> list[str]:
    prediction = model.predict(np.array([image]))
    predicted_class = np.argmax(prediction, axis=-1)
    # for each class in predicted_class read word from file imagenet_classes.txt and add to list
    result = []
    for class_id in predicted_class:
        with open('imagenet_classes.txt') as f:
            # if line starts with class_id then add to result
            for line in f:
                if line.startswith(str(class_id)):
                    result.append(line.split(' ', 1)[
                                  1].strip().replace('_', ' '))
    return result


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/users/me/images/")
async def read_own_images(current_user: User = Depends(get_current_active_user)):
    return current_user.images


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(user)
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400,
                            detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db=db, skip=skip, limit=limit)
    for user in users:
        print(user)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/images/", response_model=schemas.Image)
async def create_image_for_user(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)


):
    image = schemas.ImageCreate(path=file.filename)
    db_image = crud.get_image_by_path(db, path=image.path)
    if db_image:
        raise HTTPException(status_code=400, detail="Image already exists")

    image_nd = read_imagefile(await file.read())
    objects = get_objects_on_image(image_nd)
    return crud.create_image_with_objects(db=db, image=image, user_id=user_id, objects=objects)


@app.get("/images/", response_model=List[schemas.Image])
def read_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    images = crud.get_images(db, skip=skip, limit=limit)
    for image in images:
        print(image)
    return images


@app.post("/images/{image_id}/objects", response_model=schemas.ImageObject)
def add_object_to_image(
    image_id: int, object: str, db: Session = Depends(get_db)
):
    return crud.add_object_to_image(db=db, object=object, image_id=image_id)


@app.get("/images/{object}", response_model=List[schemas.Image])
def read_images_by_object(
    object: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    images = crud.get_images_by_object(
        db, object=object, skip=skip, limit=limit)
    return images


@app.get("/users/me/images/{object}", response_model=List[schemas.Image])
def read_own_images_by_object(
    user_id: int, object: str, current_user: User = Depends(get_current_active_user), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    # check if current_user is the same as user_id
    if crud.get_user(db, user_id) != current_user:
        raise HTTPException(status_code=403, detail="Forbidden")

    images = crud.get_own_images_by_object(
        db, object=object, skip=skip, limit=limit, user_id=user_id)
    return images


@app.get("/images/albums/", response_model=list[schemas.Album])
def read_albums(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    albums = crud.get_albums(db=db, skip=skip, limit=limit)
    return albums


@app.get("/users/me/images/albums/", response_model=list[schemas.Album])
def read_own_albums(user_id: int, current_user: User = Depends(get_current_active_user), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # check if current_user is the same as user_id
    if crud.get_user(db, user_id) != current_user:
        raise HTTPException(status_code=403, detail="Forbidden")

    albums = crud.get_own_albums(
        db=db, skip=skip, limit=limit, user_id=user_id)
    return albums


@app.post("/users/{user_id}/images/albums/", response_model=schemas.Album)
def create_album_for_user(
    user_id: int,
    album: schemas.AlbumCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # check if current_user is the same as user_id
    if crud.get_user(db, user_id) != current_user:
        raise HTTPException(status_code=403, detail="Forbidden")

    db_album = crud.get_album_by_name(db, name=album.name)
    if db_album:
        raise HTTPException(status_code=400, detail="Album already exists")
    return crud.create_album(db=db, album=album, user_id=user_id)


@app.post("/users/{user_id}/images/albums/{album_id}", response_model=schemas.Album)
def add_image_to_album(
    user_id: int,
    album_id: int,
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # check if current_user is the same as user_id
    if crud.get_user(db, user_id) != current_user:
        raise HTTPException(status_code=403, detail="Forbidden")

    db_album = crud.get_album(db, album_id)
    if db_album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    # check if album belongs to user
    if db_album.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db_image = crud.get_image(db, image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    # check if image belongs to user
    if db_image.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return crud.add_image_to_album(db=db, album_id=album_id, image_id=image_id)


@app.get("/users/me/images/favorites/", response_model=List[schemas.Favorite])
def read_own_favorite_images(user_id: int, current_user: User = Depends(get_current_active_user), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # check if current_user is the same as user_id
    if crud.get_user(db, user_id) != current_user:
        raise HTTPException(status_code=403, detail="Forbidden")

    images = crud.get_own_favorite_images(
        db=db, skip=skip, limit=limit, user_id=user_id)
    return images


@app.post("/users/{user_id}/images/{image_id}/favorites", response_model=schemas.Favorite)
def add_image_to_favorites(
    user_id: int,
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # check if current_user is the same as user_id
    if crud.get_user(db, user_id) != current_user:
        raise HTTPException(status_code=403, detail="Forbidden")

    db_image = crud.get_image(db, image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    # check if image belongs to user
    if db_image.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    # check if image is already in favorites
    if crud.get_favorite_image(db, image_id=image_id, user_id=user_id):
        raise HTTPException(
            status_code=400, detail="Image already in favorites")
    return crud.add_image_to_favorites(db=db, image_id=image_id, user_id=user_id)
