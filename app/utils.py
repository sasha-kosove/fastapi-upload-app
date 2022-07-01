from datetime import datetime, timedelta
from typing import Union
import os
import uuid

from fastapi import UploadFile, Depends, HTTPException, status
from minio import Minio
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.config import MINIO_ACCESS_KEY, MINIO_SERVER_URL, MINIO_SECRET_KEY
from app import models, crud, schemas, config, database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class MinioUploader:
    __instance = None

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = MinioUploader()
        return cls.__instance

    def __init__(self):
        self.minio_server_url = MINIO_SERVER_URL
        self.minio_access_key = MINIO_ACCESS_KEY
        self.minio_secret_key = MINIO_SECRET_KEY
        self.minio_client = Minio(
            self.minio_server_url,
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=False
        )

    def put_object(self, file: UploadFile) -> str:
        bucket_name = datetime.now().strftime("%Y%m%d")

        if not self.minio_client.bucket_exists(bucket_name):
            self.minio_client.make_bucket(bucket_name)

        file_name = str(uuid.uuid4()) + ".jpg"

        with file.file as file_data:
            self.minio_client.put_object(
                bucket_name=bucket_name,
                object_name=file_name,
                data=file_data,
                length=os.fstat(file_data.fileno()).st_size,
                content_type="image/jpeg"
            )

        return file_name

    def remove_object(self, file: models.Frame) -> None:
        self.minio_client.remove_object(
            bucket_name=file.registered_at.strftime("%Y%m%d"),
            object_name=file.frame_name,
        )

    def get_presigned_url(self, file: models.Frame) -> str:
        return self.minio_client.get_presigned_url(
            "GET",
            bucket_name=file.registered_at.strftime("%Y%m%d"),
            object_name=file.frame_name,
            expires=timedelta(hours=1)
        )


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_username(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return schemas.User(**user.__dict__)
