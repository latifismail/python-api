from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..conf import database, models, utils


router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login")
def login(payload: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if user == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid Credentials")

    if not utils.verify(payload.password, user.password):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid Credentials")

    access_token = utils.create_access_token(data = {"user_id": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
