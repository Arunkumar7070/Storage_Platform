from fastapi import APIRouter, Form,UploadFile
from fastapi.responses import StreamingResponse
from fastapi import File as FileParm
from app.database import get_database
from app.services import get_user,get_user_file,store_content,get_user_folder,delete_file
from app.models import File
from app.storage import download_object

router = APIRouter(prefix="/files", tags=["Files"])

# Upload a file
@router.post("/upload")
def upload_file(file: UploadFile = FileParm(...), user_id = Form(...), folder_id= Form(None)):
    with get_database() as db:
        user = get_user(db, user_id)
        if folder_id is not None:
            get_user_folder(db, folder_id, user)
        blob = store_content(db, file)
        new_file = File(name=file.filename, owner_id=user.id, folder_id=folder_id, blob_id=blob.id, content_type=file.content_type, size=blob.size)
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        return new_file

#List the file
@router.get("")
def list_files(user_id, folder_id = None):
    with get_database() as db:
        user = get_user(db, user_id)
        files=(db.query(File).filter(File.owner_id == user.id, File.folder_id == folder_id).order_by(File.name).all() if folder_id else db.query(File).filter(File.owner_id == user.id).order_by(File.name).all())
        return files

# Doewnload a file
@router.get("/{file_id}/download")
def download_file(file_id, user_id):
    with get_database() as db:
        user = get_user(db, user_id)
        file = get_user_file(db, file_id, user)
        file_name = file.name
        content_type = file.content_type or "application/octet-stream"
        storage_key = file.blob.storage_key
    body = download_object(storage_key)

    header = {"Content-Disposition": f"attachment; filename={file_name}"}
    return StreamingResponse(body.iter_chunks(), media_type=content_type, headers=header)

# Rename a file
@router.put("/{file_id}")
def rename_file(file_id, new_name= Form(...), user_id= Form(...)):
    with get_database() as db:
        user = get_user(db, user_id)
        file = get_user_file(db, file_id, user)
        file.name = new_name
        db.commit()
        db.refresh(file)
        return file

#Delete a file
@router.delete("/{file_id}",status_code=204)
def remove_file(file_id, user_id=Form(...)):
    with get_database() as db:
        user = get_user(db, user_id)
        file = get_user_file(db, file_id, user)
        delete_file(db, file)
     

    