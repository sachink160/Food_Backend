from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.get("/nearby")
def search_nearby(
    lat: float,
    lng: float,
    radius_km: float = Query(default=5.0, ge=0.5, le=50.0),
    db: Session = Depends(get_db),
):
    # naive circle filter using simple Pythagorean on lat/lng deltas (not accurate for large distances)
    lat_delta = radius_km / 111.0
    lng_delta = radius_km / 111.0
    q = (
        db.query(models.Restaurant)
        .filter(models.Restaurant.is_active == True)
        .filter(models.Restaurant.latitude.isnot(None), models.Restaurant.longitude.isnot(None))
        .filter(models.Restaurant.latitude.between(lat - lat_delta, lat + lat_delta))
        .filter(models.Restaurant.longitude.between(lng - lng_delta, lng + lng_delta))
        .order_by(models.Restaurant.rating.desc())
    )
    return {"success": True, "data": q.all()}


@router.get("/popular")
def search_popular(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    items = (
        db.query(models.Restaurant)
        .filter(models.Restaurant.is_active == True)
        .order_by(models.Restaurant.rating.desc(), models.Restaurant.total_reviews.desc())
        .limit(limit)
        .all()
    )
    return {"success": True, "data": items}


@router.get("/new")
def search_new(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    items = (
        db.query(models.Restaurant)
        .filter(models.Restaurant.is_active == True)
        .order_by(models.Restaurant.created_at.desc())
        .limit(limit)
        .all()
    )
    return {"success": True, "data": items}


@router.get("/code/{unique_code}")
def get_by_unique_code(unique_code: str, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.unique_code == unique_code).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True, "data": restaurant}


