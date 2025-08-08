from fastapi import FastAPI
from app.routers.uniton import router as uniton_router
from app.db.database import Base,engine
from app.routers.mqtt import router as mqtt_router
from app.mqtt.client import start_mqtt_client

app = FastAPI()

Base.metadata.create_all(bind=engine)

start_mqtt_client(app)

@app.get("/")
def read_root():
    return {"server start"}



app.include_router(mqtt_router)