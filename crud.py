from sqlalchemy.orm import Session
import models
import schemas
from utils import get_password_hash


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Image).offset(skip).limit(limit).all()


def get_images_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Image).filter(models.Image.owner_id == user_id).offset(skip).limit(limit).all()


def get_image_by_path(db: Session, path: str):
    return db.query(models.Image).filter(models.Image.path == path).first()


def create_user_image(db: Session, image: schemas.ImageCreate, user_id: int):
    db_image = models.Image(**image.dict(), owner_id=user_id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def get_images_by_object(db: Session, object: str, skip: int = 0, limit: int = 100):
    return db.query(models.Image).join(models.Image.objects).filter(models.ImageObject.object.like(f"%{object}%")).offset(skip).limit(limit).all()


def add_object_to_image(db: Session, object: str, image_id: int):
    db_object = models.ImageObject(object=object, image_id=image_id)
    db.add(db_object)
    db.commit()
    db.refresh(db_object)
    return db_object


def create_image_with_objects(db: Session, image: schemas.ImageCreate, user_id: int, objects: list[str]):
    db_image = models.Image(**image.dict(), owner_id=user_id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    for object in objects:
        db_object = models.ImageObject(object=object, image_id=db_image.id)
        db.add(db_object)
    db.commit()
    db.refresh(db_image)
    return db_image


def get_own_images_by_object(db: Session, object: str, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Image).join(models.Image.objects).filter(models.ImageObject.object.like(f"%{object}%"), models.Image.owner_id == user_id).offset(skip).limit(limit).all()


def get_albums(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Album).offset(skip).limit(limit).all()


def get_own_albums(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Album).filter(models.Album.owner_id == user_id).offset(skip).limit(limit).all()


def get_album_by_name(db: Session, name: str):
    return db.query(models.Album).filter(models.Album.name == name).first()


def create_album(db: Session, album: schemas.AlbumCreate, user_id: int):
    db_album = models.Album(**album.dict(), owner_id=user_id)
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album


def get_album(db: Session, album_id: int):
    return db.query(models.Album).filter(models.Album.id == album_id).first()


def get_image(db: Session, image_id: int):
    return db.query(models.Image).filter(models.Image.id == image_id).first()


def add_image_to_album(db: Session, album_id: int, image_id: int):
    db_album = db.query(models.Album).filter(
        models.Album.id == album_id).first()
    db_image = db.query(models.Image).filter(
        models.Image.id == image_id).first()
    db_album.images.append(db_image)
    db.commit()
    db.refresh(db_album)
    return db_album


def get_own_favorite_images(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Favorite).filter(models.Favorite.owner_id == user_id).offset(skip).limit(limit).all()


def add_image_to_favorites(db: Session, image_id: int, user_id: int):
    db_favorite = models.Favorite(image_id=image_id, owner_id=user_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


def get_favorite_image(db: Session, image_id: int, user_id: int):
    return db.query(models.Favorite).filter(models.Favorite.image_id == image_id, models.Favorite.owner_id == user_id).first()
