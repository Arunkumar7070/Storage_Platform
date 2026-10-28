from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import base, engine
from app.routers import auth,files,folders

#Create the tables only if the table does not exist
base.metadata.create_all(bind=engine)
app=FastAPI(title="Content Storage Platform")
app.add_middleware(CORSMiddleware, allow_origins=["*"],allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(files.router)
app.include_router(folders.router)

# Health check endpoint
@app.get("/")
def health_check():
    return {"message": "Content Storage Platform is running!"}
