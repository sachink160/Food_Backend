from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter()


def get_my_restaurant(db: Session, owner_id: int) -> models.Restaurant | None:
    return db.query(models.Restaurant).filter(models.Restaurant.owner_id == owner_id).first()


@router.post("/restaurant", response_model=dict, summary="Create or update my restaurant")
def create_or_update_my_restaurant(
    payload: schemas.RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    restaurant = get_my_restaurant(db, current_user.id)
    if restaurant:
        # update
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(restaurant, k, v)
    else:
        restaurant = models.Restaurant(owner_id=current_user.id, **payload.model_dump())
        db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    # Convert SQLAlchemy model to Pydantic schema for proper serialization
    restaurant_data = schemas.RestaurantResponse.model_validate(restaurant).model_dump()
    return {"success": True, "data": restaurant_data}
@router.post("/restaurant/upload-image", response_model=dict, summary="Upload restaurant image (owner)")
def upload_restaurant_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    restaurant = get_my_restaurant(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=400, detail="Create restaurant first")

    # Validate content type
    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    uploads_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
    os.makedirs(uploads_root, exist_ok=True)

    ext = os.path.splitext(image.filename or "")[1].lower() or ".jpg"
    filename = f"restaurant_{restaurant.id}_{int(datetime.utcnow().timestamp())}{ext}"
    filepath = os.path.join(uploads_root, filename)

    with open(filepath, "wb") as f:
        f.write(image.file.read())

    public_url = f"/uploads/{filename}"
    restaurant.image_url = public_url
    db.commit()
    db.refresh(restaurant)

    data = schemas.RestaurantResponse.model_validate(restaurant).model_dump()
    return {"success": True, "data": data}


@router.get("/restaurant", response_model=dict, summary="Get my restaurant details")
def get_my_restaurant_endpoint(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    restaurant = get_my_restaurant(db, current_user.id)
    if not restaurant:
        # Return success with null data to allow frontend to render creation UI
        return {"success": True, "data": None}
    # Convert SQLAlchemy model to Pydantic schema for proper serialization
    restaurant_data = schemas.RestaurantResponse.model_validate(restaurant).model_dump()
    return {"success": True, "data": restaurant_data}


# Category management
@router.post("/restaurant/categories")
def create_category(
    payload: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    restaurant = get_my_restaurant(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=400, detail="Create restaurant first")
    category = models.Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    # Convert SQLAlchemy model to Pydantic schema for proper serialization
    category_data = schemas.CategoryResponse.model_validate(category).model_dump()
    return {"success": True, "data": category_data}


@router.get("/restaurant/categories")
def list_categories(db: Session = Depends(get_db)):
    items = db.query(models.Category).filter(models.Category.is_active == True).all()
    # Convert SQLAlchemy models to Pydantic schemas for proper serialization
    items_data = [schemas.CategoryResponse.model_validate(item).model_dump() for item in items]
    return {"success": True, "data": items_data}


@router.patch("/restaurant/categories/{category_id}")
def update_category(
    category_id: int,
    payload: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    category = db.query(models.Category).get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(category, k, v)
    db.commit()
    db.refresh(category)
    # Convert SQLAlchemy model to Pydantic schema for proper serialization
    category_data = schemas.CategoryResponse.model_validate(category).model_dump()
    return {"success": True, "data": category_data}


@router.delete("/restaurant/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"success": True, "data": {"detail": "Deleted"}}


@router.post("/restaurant/categories/{category_id}/upload-image", response_model=dict, summary="Upload category image")
def upload_category_image(
    category_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    category = db.query(models.Category).get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    uploads_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
    os.makedirs(uploads_root, exist_ok=True)

    ext = os.path.splitext(image.filename or "")[1].lower() or ".jpg"
    filename = f"category_{category.id}_{int(datetime.utcnow().timestamp())}{ext}"
    filepath = os.path.join(uploads_root, filename)

    with open(filepath, "wb") as f:
        f.write(image.file.read())

    category.image_url = f"/uploads/{filename}"
    db.commit()
    db.refresh(category)

    data = schemas.CategoryResponse.model_validate(category).model_dump()
    return {"success": True, "data": data}


# Menu items for my restaurant
@router.post("/restaurant/menu")
def create_menu_item(
    payload: schemas.MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    restaurant = get_my_restaurant(db, current_user.id)
    if not restaurant or restaurant.id != payload.restaurant_id:
        raise HTTPException(status_code=400, detail="Invalid restaurant for user")
    item = models.MenuItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    # Convert SQLAlchemy model to Pydantic schema for proper serialization
    item_data = schemas.MenuItemResponse.model_validate(item).model_dump()
    return {"success": True, "data": item_data}


@router.post("/restaurant/menu/{item_id}/upload-image", response_model=dict, summary="Upload menu item image")
def upload_menu_item_image(
    item_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    restaurant = get_my_restaurant(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=400, detail="Create restaurant first")
    item = (
        db.query(models.MenuItem)
        .filter(models.MenuItem.id == item_id, models.MenuItem.restaurant_id == restaurant.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    uploads_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
    os.makedirs(uploads_root, exist_ok=True)

    ext = os.path.splitext(image.filename or "")[1].lower() or ".jpg"
    filename = f"menuitem_{item.id}_{int(datetime.utcnow().timestamp())}{ext}"
    filepath = os.path.join(uploads_root, filename)

    with open(filepath, "wb") as f:
        f.write(image.file.read())

    item.image_url = f"/uploads/{filename}"
    db.commit()
    db.refresh(item)

    data = schemas.MenuItemResponse.model_validate(item).model_dump()
    return {"success": True, "data": data}


@router.get("/restaurant/menu")
def list_menu_items(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    restaurant = get_my_restaurant(db, current_user.id)
    if not restaurant:
        # No restaurant yet; return empty list for a graceful UX
        return {"success": True, "data": []}
    items = (
        db.query(models.MenuItem)
        .filter(models.MenuItem.restaurant_id == restaurant.id)
        .all()
    )
    # Convert SQLAlchemy models to Pydantic schemas for proper serialization
    items_data = [schemas.MenuItemResponse.model_validate(item).model_dump() for item in items]
    return {"success": True, "data": items_data}


@router.patch("/restaurant/menu/{item_id}")
def update_menu_item(
    item_id: int,
    payload: schemas.MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    restaurant = get_my_restaurant(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=400, detail="Create restaurant first")
    item = (
        db.query(models.MenuItem)
        .filter(models.MenuItem.id == item_id, models.MenuItem.restaurant_id == restaurant.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    # Convert SQLAlchemy model to Pydantic schema for proper serialization
    item_data = schemas.MenuItemResponse.model_validate(item).model_dump()
    return {"success": True, "data": item_data}


@router.delete("/restaurant/menu/{item_id}")
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    restaurant = get_my_restaurant(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=400, detail="Create restaurant first")
    item = (
        db.query(models.MenuItem)
        .filter(models.MenuItem.id == item_id, models.MenuItem.restaurant_id == restaurant.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()
    return {"success": True, "data": {"detail": "Deleted"}}


# Special items management using Restaurant.special_items JSON field
@router.get("/restaurant/specials")
def get_specials(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    restaurant = get_my_restaurant(db, current_user.id)
    if not restaurant:
        # No restaurant yet; no specials
        return {"success": True, "data": []}
    return {"success": True, "data": (restaurant.special_items or [])}


@router.post("/restaurant/specials")
def set_specials(
    specials: list[int],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    restaurant = get_my_restaurant(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=400, detail="Create restaurant first")
    restaurant.special_items = specials
    db.commit()
    db.refresh(restaurant)
    return {"success": True, "data": restaurant.special_items}


