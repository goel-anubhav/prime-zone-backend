from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
import shutil
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid


from app.db.session import get_session
from app.db.models import Service, User
from app.db.schema import ServiceCreate, ServiceUpdate, ServiceResponse, BaseOutput
from app.routes.auth import get_active_user
from app.db.enum import UserType

router = APIRouter()

STATIC_DIR = "static"

async def check_admin(user: User = Depends(get_active_user)):
    if user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins can perform this action"
        )
    return user

@router.get("/", response_model=List[ServiceResponse])
async def get_all_services(
    db: AsyncSession = Depends(get_session),
    # user: User = Depends(check_admin)
):
    result = await db.execute(select(Service))
    services = result.scalars().all()
    return services

@router.get("/{id}", response_model=ServiceResponse)
async def get_service(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):
    result = await db.execute(select(Service).where(Service.id == id))
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("/", response_model=ServiceResponse)
async def create_service(
    title: str = Form(...),
    category: Optional[str] = Form(None),
    heading1: Optional[str] = Form(None),
    heading2: Optional[str] = Form(None),
    detail1: Optional[str] = Form(None),
    detail2: Optional[str] = Form(None),
    image1: UploadFile = File(None),
    image2: UploadFile = File(None),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):  
    image1_url = None
    image2_url = None

    try:
        if image1:
            file_extension = image1.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(STATIC_DIR, file_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image1.file, buffer)
            
            image1_url = f"/static/{file_name}"
        
        if image2:
            file_extension = image2.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(STATIC_DIR, file_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image2.file, buffer)
            
            image2_url = f"/static/{file_name}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    new_service = Service(
        title=title,
        category=category,
        heading1=heading1,
        heading2=heading2,
        detail1=detail1,
        detail2=detail2,
        image1=image1_url,
        image2=image2_url
    )
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)
    return new_service

@router.put("/{id}", response_model=ServiceResponse)
async def update_service(
    id: uuid.UUID,
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    heading1: Optional[str] = Form(None),
    heading2: Optional[str] = Form(None),
    detail1: Optional[str] = Form(None),
    detail2: Optional[str] = Form(None),
    image1: Optional[UploadFile] = File(None),
    image2: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):
    result = await db.execute(select(Service).where(Service.id == id))
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if title is not None:
        service.title = title
    if category is not None:
        service.category = category
    if heading1 is not None:
        service.heading1 = heading1
    if heading2 is not None:
        service.heading2 = heading2
    if detail1 is not None:
        service.detail1 = detail1
    if detail2 is not None:
        service.detail2 = detail2

    try:
        if image1:
            # Delete old image1 if exists
            if service.image1:
                relative_path = service.image1.lstrip("/")
                old_file_path = relative_path  # Assuming static is in root or handled correctly
                # We might need to adjust path if static is not in current working dir
                # but based on provided code, os.path.join(STATIC_DIR) was used.
                # Let's be consistent with delete logic.
                
                # The create logic uses: os.path.join(STATIC_DIR, file_name)
                # The url is: /static/filename
                # So to get path: remove /static/ and join with STATIC_DIR? 
                
                # Previous code did: service.image.lstrip("/") -> static/filename
                if os.path.exists(relative_path):
                     os.remove(relative_path)

            file_extension = image1.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(STATIC_DIR, file_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image1.file, buffer)
            
            service.image1 = f"/static/{file_name}"
            
        if image2:
            # Delete old image2 if exists
            if service.image2:
                relative_path = service.image2.lstrip("/")
                if os.path.exists(relative_path):
                     os.remove(relative_path)

            file_extension = image2.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(STATIC_DIR, file_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image2.file, buffer)
            
            service.image2 = f"/static/{file_name}"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
    
    await db.commit()
    await db.refresh(service)
    return service

@router.delete("/{id}", response_model=BaseOutput)
async def delete_service(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):
    result = await db.execute(select(Service).where(Service.id == id))
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Delete Images from Static Folder
    if service.image1:
        relative_path = service.image1.lstrip("/")
        if os.path.exists(relative_path):
            os.remove(relative_path)
            
    if service.image2:
        relative_path = service.image2.lstrip("/")
        if os.path.exists(relative_path):
            os.remove(relative_path)

    await db.delete(service)
    await db.commit()
    return BaseOutput(message="Service deleted successfully", detail=f"Service with id {id} has been deleted")
