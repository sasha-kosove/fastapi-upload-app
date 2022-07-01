from typing import List
from sqlalchemy.orm import Session

from app import models
from app import schemas


def create_frame(db: Session, frame: schemas.FrameCreate):
    db_frame = models.Frame(**frame.dict())
    db.add(db_frame)
    db.commit()
    db.refresh(db_frame)
    return db_frame


def get_frame_by_id(db: Session, frame_ids: List[int]):
    return db.query(models.Frame).filter(models.Frame.id.in_(frame_ids)).all()


def remove_frame(db: Session, frame_ids: List[int]):
    db.query(models.Frame).filter(models.Frame.id.in_(frame_ids)).delete(synchronize_session=False)
    db.commit()


def create_user(db: Session, user: schemas.UserAuth):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
