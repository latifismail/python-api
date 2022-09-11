from fastapi import FastAPI

from .routes import post, user, auth
from .conf import database, models


models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
