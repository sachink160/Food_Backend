from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=dict, summary="Get current user profile")
def get_me(current_user: models.User = Depends(get_current_user)):
    user_data = schemas.UserResponse.model_validate(current_user).model_dump()
    return {"success": True, "data": user_data}


@router.patch("/me", response_model=dict, summary="Update current user profile")
def update_me(
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(current_user, k, v)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    user_data = schemas.UserResponse.model_validate(current_user).model_dump()
    return {"success": True, "data": user_data}


# Address management for current user
@router.get("/me/addresses")
def list_addresses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    items = (
        db.query(models.UserAddress)
        .filter(models.UserAddress.user_id == current_user.id)
        .all()
    )
    data = [schemas.AddressResponse.model_validate(a).model_dump() for a in items]
    return {"success": True, "data": data}


@router.post("/me/addresses")
def create_address(
    payload: schemas.AddressCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    address = models.UserAddress(user_id=current_user.id, **payload.model_dump())
    if address.is_default:
        # unset previous default
        db.query(models.UserAddress).filter(
            models.UserAddress.user_id == current_user.id,
            models.UserAddress.is_default == True,
        ).update({models.UserAddress.is_default: False})
    db.add(address)
    db.commit()
    db.refresh(address)
    addr_data = schemas.AddressResponse.model_validate(address).model_dump()
    return {"success": True, "data": addr_data}


@router.patch("/me/addresses/{address_id}")
def update_address(
    address_id: int,
    payload: schemas.AddressUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    address = (
        db.query(models.UserAddress)
        .filter(models.UserAddress.id == address_id, models.UserAddress.user_id == current_user.id)
        .first()
    )
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    data = payload.model_dump(exclude_unset=True)
    if data.get("is_default"):
        db.query(models.UserAddress).filter(
            models.UserAddress.user_id == current_user.id,
            models.UserAddress.is_default == True,
            models.UserAddress.id != address.id,
        ).update({models.UserAddress.is_default: False})
    for k, v in data.items():
        setattr(address, k, v)
    db.commit()
    db.refresh(address)
    addr_data = schemas.AddressResponse.model_validate(address).model_dump()
    return {"success": True, "data": addr_data}


@router.delete("/me/addresses/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    address = (
        db.query(models.UserAddress)
        .filter(models.UserAddress.id == address_id, models.UserAddress.user_id == current_user.id)
        .first()
    )
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(address)
    db.commit()
    return {"success": True, "data": {"detail": "Deleted"}}


