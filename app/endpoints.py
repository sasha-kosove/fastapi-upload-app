from datetime import timedelta, datetime
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, Query, Response, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import database, crud, schemas, utils, config

router = APIRouter()


@router.post("/frames/", status_code=status.HTTP_201_CREATED, response_model=List[schemas.Frame])
async def upload_frames(
        frames: List[UploadFile] = File(...),
        db: Session = Depends(database.get_db),
        current_user: schemas.User = Depends(utils.get_current_user)
):
    if len(frames) > 15:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Too many files to upload")
    results = list()
    for frame in frames:
        frame_name = utils.MinioUploader.get_instance().put_object(frame)
        db_frame = crud.create_frame(
            db=db,
            frame=schemas.FrameCreate(frame_name=frame_name, registered_at=datetime.now())
        )
        results.append(db_frame)
    return results


@router.get("/frames/", response_model=List[schemas.FrameOut])
async def read_frames(
    id: Union[List[int], None] = Query(),
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(utils.get_current_user)
):
    results = [schemas.FrameOut(
        **frame.__dict__,
        url=utils.MinioUploader.get_instance().get_presigned_url(frame)
    ) for frame in crud.get_frame_by_id(db=db, frame_ids=id)]
    return results


@router.delete("/frames/")
async def delete_frames(
    id: List[int] = Query(),
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(utils.get_current_user)
):
    for frame in crud.get_frame_by_id(db=db, frame_ids=id):
        utils.MinioUploader.get_instance().remove_object(frame)
    crud.remove_frame(db=db, frame_ids=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    user = utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signup")
async def sign_up(user: schemas.UserAuth, db: Session = Depends(database.get_db)):
    exists_user = crud.get_user_by_username(db=db, username=user.username)
    if exists_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    hashed_password = utils.get_password_hash(user.hashed_password)
    user.hashed_password = hashed_password
    crud.create_user(db, user)
    return {"message": "Created user successfully!"}


@router.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(utils.get_current_user)):
    return current_user
