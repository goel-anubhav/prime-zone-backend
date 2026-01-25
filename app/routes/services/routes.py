from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.db.session import get_session
from app.db.models import Service, User
from app.db.schema import ServiceCreate, ServiceUpdate, ServiceResponse, BaseOutput
from app.routes.auth import get_active_user
from app.db.enum import UserType

router = APIRouter()

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
    service: ServiceCreate,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):
    new_service = Service(**service.model_dump())
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)
    return new_service

@router.put("/{id}", response_model=ServiceResponse)
async def update_service(
    id: uuid.UUID,
    service_update: ServiceUpdate,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(check_admin)
):
    result = await db.execute(select(Service).where(Service.id == id))
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    for key, value in service_update.model_dump(exclude_unset=True).items():
        setattr(service, key, value)
    
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
    
    await db.delete(service)
    await db.commit()
    return BaseOutput(message="Service deleted successfully", detail=f"Service with id {id} has been deleted")
