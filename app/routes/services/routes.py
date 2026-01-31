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
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(Service))
    services = result.scalars().all()
    return services

@router.get("/{id}", response_model=ServiceResponse)
async def get_service(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(Service).where(Service.id == id))
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("/", response_model=ServiceResponse)
async def create_service(
    title: str = Form(...),
    category: str = Form(...),
    details: str = Form(None),
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):  
    image_url = None
    if image:
        try:
            file_extension = image.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(STATIC_DIR, file_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            image_url = f"/static/{file_name}"
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    new_service = Service(
        title=title,
        category=category,
        details=details,
        image=image_url
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
    details: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
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
    if details is not None:
        service.details = details

    if image:
        try:
            # Delete old image if exists
            if service.image:
                relative_path = service.image.lstrip("/")
                old_file_path = relative_path
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            file_extension = image.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(STATIC_DIR, file_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            service.image = f"/static/{file_name}"
        
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
    
    # Delete Image from Static Folder
    if service.image:
        relative_path = service.image.lstrip("/")
        file_path = relative_path
        if os.path.exists(file_path):
            os.remove(file_path)

    await db.delete(service)
    await db.commit()
    return BaseOutput(message="Service deleted successfully", detail=f"Service with id {id} has been deleted")
