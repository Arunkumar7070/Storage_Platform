import hashlib
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models import User, File, Folder, Blob
from app.storage import delete_object,upload_object

# 1mb
chunk_size = 1024 * 1024

# find the user by user ID
def get_user(db, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# folder only belongs to that partucular  user
def get_user_folder(db,folder_id,user):
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.owner_id == user.id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder   

# get the file for a specific usee
def get_user_file(db,file_id,user):
    file = db.query(File).filter(File.id == file_id, File.owner_id == user.id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file

# hashing the file content to get the sha256 hash and return the size of the file 
def calculate_sha256(file):
    sha256 = hashlib.sha256()
    size = 0
    # Read the file in chunks to avoid loading the entire file into memory
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        sha256.update(chunk)
        size += len(chunk)
    # Reset the file pointer to the beginning
    file.seek(0)  
    return sha256.hexdigest(),size

# storage optimization Duplicate detection
def store_content(db,upload):
    sha256_hash, size = calculate_sha256(upload.file)
    existing_blob = db.query(Blob).filter(Blob.sha256 == sha256_hash).first()
    if existing_blob:
        return existing_blob  
    storage_key=f"blobs/{sha256_hash}"
    upload_object(storage_key,upload.file,upload.content_type)
    blob=Blob(sha256=sha256_hash,size=size,storage_key=storage_key)
    db.add(blob)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return db.query(Blob).filter(Blob.sha256 == sha256_hash).first()
    db.refresh(blob)
    return blob

#Remove the blob if no files are referencing it
def release_blob(db,blob_id):
    rem=db.query(File).filter(File.blob_id==blob_id).count()
    if rem>0:
        return
    blob=db.query(Blob).filter(Blob.id==blob_id).first()
    if blob:
        delete_object(blob.storage_key)
        db.delete(blob)
        db.commit()

# Dele the file
def delete_file(db,file):
    blob_id=file.blob_id
    db.delete(file)
    db.commit()
    release_blob(db,blob_id)

# Delete the folder 
def delete_folder_tree(db,folder):
    children_folder=db.query(Folder).filter(Folder.parent_id==folder.id).all()
    for c in children_folder:
        delete_folder_tree(db,c)
    files=db.query(File).filter(File.folder_id==folder.id).all()
    for f in files:
        delete_file(db,f)
    db.delete(folder)
    db.commit()
