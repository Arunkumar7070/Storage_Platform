from fastapi import APIRouter,Form
from app.database import get_database
from app.models import Folder,File
from app.services import get_user,get_user_folder,delete_folder_tree

router = APIRouter(prefix="/folders", tags=["Folders"])

# Create a new folder
@router.post("")
def create_folder(name=Form(...), user_id=Form(...), parent_id=Form(None)):
    with get_database() as db:
        user = get_user(db, user_id)
        if parent_id is not None:
            get_user_folder(db, parent_id, user)
        new_folder = Folder(name=name, owner_id=user.id, parent_id=parent_id)
        db.add(new_folder)
        db.commit()
        db.refresh(new_folder)
        return new_folder


# List the what is inside the folder
@router.get("/contents")
def list_folder_contents(user_id, folder_id = None):
    with get_database() as db:
        user = get_user(db, user_id)
        folder=None
        if folder_id is not None:
            folder = get_user_folder(db, folder_id, user)
        subfolders = db.query(Folder).filter(Folder.owner_id == user.id, Folder.parent_id == folder_id).order_by(Folder.name).all()
        files = db.query(File).filter(File.owner_id == user.id, File.folder_id == folder_id).order_by(File.name).all()
        return {"folder": folder, "subfolders": subfolders, "files": files}

# Rename a folder
@router.put("/{folder_id}")
def rename_folder(folder_id,name=Form(...), user_id=Form(...)):
    with get_database() as db:
        user = get_user(db, user_id)
        folder = get_user_folder(db, folder_id, user)
        folder.name = name
        db.commit()
        db.refresh(folder)
        return folder

# Delete a folder
@router.delete("/{folder_id}",status_code=204)
def remove_folder(folder_id, user_id=Form(...)):
    with get_database() as db:
        user = get_user(db, user_id)
        folder = get_user_folder(db, folder_id, user)
        delete_folder_tree(db, folder)
