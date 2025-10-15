from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/")
def create_restaurant(payload: schemas.RestaurantCreate, db: Session = Depends(get_db)):
    owner = db.query(models.User).first()
    if not owner:
        raise HTTPException(status_code=400, detail="Owner user required to create restaurant")

    restaurant = models.Restaurant(
        owner_id=owner.id,
        **payload.model_dump()
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return {"success": True, "data": restaurant}

@router.get("/")
def list_restaurants(
    city: Optional[str] = None,
    cuisine: Optional[str] = Query(None, alias="cuisine_type"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Restaurant).filter(models.Restaurant.is_active == True)
    if city:
        query = query.filter(models.Restaurant.city.ilike(f"%{city}%"))
    if cuisine:
        query = query.filter(models.Restaurant.cuisine_type.ilike(f"%{cuisine}%"))
    items = query.order_by(models.Restaurant.rating.desc()).all()
    return {"success": True, "data": items}

@router.get("/{restaurant_id}")
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).get(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return {"success": True, "data": restaurant}

@router.patch("/{restaurant_id}")
def update_restaurant(restaurant_id: int, payload: schemas.RestaurantUpdate, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).get(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(restaurant, k, v)
    db.commit()
    db.refresh(restaurant)
    return {"success": True, "data": restaurant}

@router.delete("/{restaurant_id}")
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).get(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    db.delete(restaurant)
    db.commit()
    return {"success": True, "data": {"detail": "Deleted"}}


