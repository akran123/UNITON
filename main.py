from fastapi import FastAPI
from routers.uniton import router as uniton_router
from database import Base,engine

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(uniton_router)