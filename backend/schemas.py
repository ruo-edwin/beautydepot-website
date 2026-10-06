from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

# ============================================================
# CATEGORY
# ============================================================

class CategoryBase(BaseModel):
    name: str
    slug: str
    image: Optional[str] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SUBCATEGORY
# ============================================================

class SubcategoryBase(BaseModel):
    name: str
    slug: str
    category_id: int
    image: Optional[str] = None
    is_active: bool = True


class SubcategoryCreate(SubcategoryBase):
    pass


class SubcategoryResponse(SubcategoryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# BRAND
# ============================================================

class BrandBase(BaseModel):
    name: str
    slug: str
    logo: Optional[str] = None
    is_active: bool = True


class BrandCreate(BrandBase):
    pass


class BrandResponse(BrandBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# PRODUCT
# ============================================================

class ProductBase(BaseModel):
    name: str
    slug: str
    sku: Optional[str] = None

    brand_id: Optional[int] = None
    category_id: int
    subcategory_id: int

    short_description: Optional[str] = None
    description: Optional[str] = None

    price: Decimal
    sale_price: Optional[Decimal] = None

    image: Optional[str] = None

    is_available: bool = True
    is_featured: bool = False
    is_new_arrival: bool = False


class ProductCreate(ProductBase):
    pass

class ProductBulkCreate(BaseModel):
    products: list[ProductCreate]

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    brand: Optional[BrandResponse] = None

    model_config = ConfigDict(from_attributes=True)

class AdminLogin(BaseModel):
    email: str
    password: str


class AdminResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    delivery_address: str
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    delivery_address: str
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)