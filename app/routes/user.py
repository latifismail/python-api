from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from ...conf import database, models, schemas, utils


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(payload: schemas.UserCreate, db: Session = Depends(database.get_db)):
    try:

        hashed_password =  utils.bcrypt_hash(payload.password)
        payload.password = hashed_password

        user = models.User(**payload.dict())

        db.add(user)
        db.commit()
        db.refresh(user)

        return user
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User or Email already exist")

@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User does not exist")

    return user
