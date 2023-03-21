from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint, Table
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
    albums = relationship("Album", back_populates="owner")
    favorites = relationship("Favorite", back_populates="owner")

    __str__ = __repr__ = lambda self: f"User(id={self.id}, username={self.username}, email={self.email}, hashed_password={self.hashed_password}, is_active={self.is_active})"


album_image_association_table = Table(
    "album_image_association_table",
    Base.metadata,
    Column("album_id", ForeignKey("albums.id")),
    Column("image_id", ForeignKey("images.id")),
)


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="images")
    objects = relationship("ImageObject", back_populates="images")
    __table_args__ = (UniqueConstraint(
        'path', 'owner_id', name='_path_owner_uc'),)

    __str__ = __repr__ = lambda self: f"Image(id={self.id}, path={self.path}, owner_id={self.owner_id})"


class ImageObject(Base):
    __tablename__ = "image_objects"

    id = Column(Integer, primary_key=True, index=True)
    object = Column(String, index=True)
    image_id = Column(Integer, ForeignKey("images.id"))

    images = relationship("Image", back_populates="objects")

    __str__ = __repr__ = lambda self: f"ImageObject(id={self.id}, name={self.name})"


class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="albums")
    images = relationship("Image", secondary=album_image_association_table)
    __table_args__ = (UniqueConstraint(
        'name', 'owner_id', name='_name_owner_uc'),)

    __str__ = __repr__ = lambda self: f"Album(id={self.id}, name={self.name}, owner_id={self.owner_id})"


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    image_id = Column(Integer, ForeignKey("images.id"))

    owner = relationship("User", back_populates="favorites")
    __table_args__ = (UniqueConstraint(
        'owner_id', 'image_id', name='_owner_image_uc'),)

    __str__ = __repr__ = lambda self: f"Favorite(id={self.id}, user_id={self.user_id}, album_id={self.album_id})"
