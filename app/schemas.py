from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.models import UserRole, OrderStatus, PaymentStatus

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        use_enum_values = True

# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    role: UserRole
    roles: List[UserRole]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserLogin(BaseSchema):
    email: EmailStr
    password: str

# Address schemas
class AddressBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=100)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(default="India", max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    address_line1: Optional[str] = Field(None, min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: Optional[bool] = None

class AddressResponse(AddressBase):
    id: int
    user_id: int
    created_at: datetime

# Restaurant schemas
class RestaurantBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cuisine_type: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    image_url: Optional[str] = Field(None, max_length=500)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    closing_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    delivery_radius: float = Field(default=5.0, ge=0.1, le=50.0)
    delivery_fee: float = Field(default=0.0, ge=0.0)
    minimum_order_amount: float = Field(default=0.0, ge=0.0)

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    cuisine_type: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    image_url: Optional[str] = Field(None, max_length=500)
    address_line1: Optional[str] = Field(None, min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    closing_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    delivery_radius: Optional[float] = Field(None, ge=0.1, le=50.0)
    delivery_fee: Optional[float] = Field(None, ge=0.0)
    minimum_order_amount: Optional[float] = Field(None, ge=0.0)
    is_active: Optional[bool] = None

class RestaurantResponse(RestaurantBase):
    id: int
    owner_id: int
    rating: float
    total_reviews: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

# Category schemas
class CategoryBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime

# Menu Item schemas
class MenuItemBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    is_vegetarian: bool = False
    is_available: bool = True
    preparation_time: Optional[int] = Field(None, ge=1, le=300)  # 1-300 minutes
    calories: Optional[int] = Field(None, ge=0)
    ingredients: Optional[List[str]] = None
    allergens: Optional[List[str]] = None

class MenuItemCreate(MenuItemBase):
    restaurant_id: int
    category_id: int

class MenuItemUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    is_vegetarian: Optional[bool] = None
    is_available: Optional[bool] = None
    preparation_time: Optional[int] = Field(None, ge=1, le=300)
    calories: Optional[int] = Field(None, ge=0)
    ingredients: Optional[List[str]] = None
    allergens: Optional[List[str]] = None

class MenuItemResponse(MenuItemBase):
    id: int
    restaurant_id: int
    category_id: int
    rating: float
    total_reviews: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Order schemas
class OrderItemCreate(BaseSchema):
    menu_item_id: int
    quantity: int = Field(..., ge=1, le=10)
    special_instructions: Optional[str] = None

class OrderCreate(BaseSchema):
    restaurant_id: int
    delivery_address: Dict[str, Any]
    special_instructions: Optional[str] = None
    order_items: List[OrderItemCreate] = Field(..., min_items=1)

class OrderUpdate(BaseSchema):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    special_instructions: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None

class OrderItemResponse(BaseSchema):
    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    unit_price: float
    total_price: float
    special_instructions: Optional[str] = None
    created_at: datetime

class OrderResponse(BaseSchema):
    id: int
    user_id: int
    restaurant_id: int
    order_number: str
    status: OrderStatus
    subtotal: float
    delivery_fee: float
    tax_amount: float
    total_amount: float
    payment_status: PaymentStatus
    delivery_address: Dict[str, Any]
    special_instructions: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    order_items: List[OrderItemResponse] = []

# Review schemas
class ReviewCreate(BaseSchema):
    restaurant_id: int
    order_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    food_rating: Optional[int] = Field(None, ge=1, le=5)
    delivery_rating: Optional[int] = Field(None, ge=1, le=5)

class ReviewUpdate(BaseSchema):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    food_rating: Optional[int] = Field(None, ge=1, le=5)
    delivery_rating: Optional[int] = Field(None, ge=1, le=5)

class ReviewResponse(BaseSchema):
    id: int
    user_id: int
    restaurant_id: int
    order_id: int
    rating: int
    comment: Optional[str] = None
    food_rating: Optional[int] = None
    delivery_rating: Optional[int] = None
    created_at: datetime

# Cart schemas
class CartItemCreate(BaseSchema):
    menu_item_id: int
    quantity: int = Field(..., ge=1, le=10)
    special_instructions: Optional[str] = None

class CartItemUpdate(BaseSchema):
    quantity: Optional[int] = Field(None, ge=1, le=10)
    special_instructions: Optional[str] = None

class CartItemResponse(BaseSchema):
    id: int
    cart_id: int
    menu_item_id: int
    quantity: int
    special_instructions: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class CartResponse(BaseSchema):
    id: int
    user_id: int
    restaurant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    cart_items: List[CartItemResponse] = []

# Token schemas
class Token(BaseSchema):
    access_token: str
    token_type: str

class TokenData(BaseSchema):
    email: Optional[str] = None

# Pagination schemas
class PaginationParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)

class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# Error schemas
class ErrorResponse(BaseSchema):
    detail: str
    error_code: Optional[str] = None

class ValidationErrorResponse(BaseSchema):
    detail: List[Dict[str, Any]]

