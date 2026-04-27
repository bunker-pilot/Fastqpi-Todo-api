from fastapi import FastAPI
from fastapi_swagger import patch_fastapi
import models
from database import engine
from routers import auth, todos



app = FastAPI(docs_url=None,swagger_ui_oauth2_redirect_url=None)
patch_fastapi(app,docs_url="/api/docs")

models.Base.metadata.create_all(bind = engine)




app.include_router(auth.router)
app.include_router(todos.router)
