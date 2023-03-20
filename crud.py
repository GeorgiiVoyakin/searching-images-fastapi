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
    return db.query(models.Image).join(models.Image.objects).filter(models.ImageObject.object == object).offset(skip).limit(limit).all()


def add_object_to_image(db: Session, object: str, image_id: int):
    db_object = models.ImageObject(object=object, image_id=image_id)
    db.add(db_object)
    db.commit()
    db.refresh(db_object)
    return db_object
