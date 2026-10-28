from sqlalchemy import Column, Integer, String, ForeignKey,String, DateTime, func,BigInteger
from sqlalchemy.orm import relationship
from app.database import base

# User model
class User(base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username=Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime,server_default=func.now())


# File model
class File(base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    blob_id = Column(Integer,ForeignKey("blobs.id"), nullable=False)
    content_type = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    blob = relationship("Blob")


# Folder model
class Folder(base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# Blob model
class Blob(base):
    __tablename__ = "blobs"
    id = Column(Integer, primary_key=True)
    sha256=Column(String(64), unique=True, nullable=False)
    size = Column(BigInteger, nullable=False)
    storage_key = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())