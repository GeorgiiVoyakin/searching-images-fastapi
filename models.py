from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, PickleType
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    images = relationship("Image", back_populates="owner")

    __str__ = __repr__ = lambda self: f"User(id={self.id}, username={self.username}, email={self.email}, hashed_password={self.hashed_password}, is_active={self.is_active})"


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, index=True, unique=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="images")
    objects = relationship("ImageObject", back_populates="images")


class ImageObject(Base):
    __tablename__ = "image_objects"

    id = Column(Integer, primary_key=True, index=True)
    object = Column(String, index=True)
    image_id = Column(Integer, ForeignKey("images.id"))

    images = relationship("Image", back_populates="objects")

    __str__ = __repr__ = lambda self: f"ImageObject(id={self.id}, name={self.name})"
