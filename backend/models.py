from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from backend.db import Base




# ============================================================
# CATEGORY
# ============================================================

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False, unique=True)

    slug = Column(String(120), nullable=False, unique=True, index=True)

    image = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # One category can have many subcategories
    subcategories = relationship(
        "Subcategory",
        back_populates="category",
        cascade="all, delete-orphan"
    )

    # One category can have many products
    products = relationship(
        "Product",
        back_populates="category"
    )


# ============================================================
# SUBCATEGORY
# ============================================================

class Subcategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    slug = Column(String(120), nullable=False, index=True)

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False,
        index=True
    )

    image = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship back to category
    category = relationship(
        "Category",
        back_populates="subcategories"
    )

    # One subcategory can have many products
    products = relationship(
        "Product",
        back_populates="subcategory"
    )


# ============================================================
# BRAND
# ============================================================

class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False, unique=True)

    slug = Column(String(180), nullable=False, unique=True, index=True)

    logo = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # One brand can have many products
    products = relationship(
        "Product",
        back_populates="brand"
    )


# ============================================================
# PRODUCT
# ============================================================

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(255),
        nullable=False,
        index=True
    )

    slug = Column(
        String(280),
        nullable=False,
        unique=True,
        index=True
    )

    sku = Column(
        String(100),
        nullable=True,
        unique=True,
        index=True
    )

    description = Column(
        Text,
        nullable=True
    )

    price = Column(
        Numeric(10, 2),
        nullable=False
    )

    sale_price = Column(
        Numeric(10, 2),
        nullable=True
    )


    brand_id = Column(
        Integer,
        ForeignKey("brands.id"),
        nullable=True,
        index=True
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False,
        index=True
    )

    subcategory_id = Column(
        Integer,
        ForeignKey("subcategories.id"),
        nullable=False,
        index=True
    )


    image = Column(
        String(255),
        nullable=True
    )

    is_available = Column(
        Boolean,
        default=True,
        nullable=False
    )

    is_featured = Column(
        Boolean,
        default=False,
        nullable=False
    )

    is_new_arrival = Column(
        Boolean,
        default=False,
        nullable=False
    )

    # --------------------------------------------------------
    # TIMESTAMPS
    # --------------------------------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    brand = relationship(
        "Brand",
        back_populates="products"
    )

    category = relationship(
        "Category",
        back_populates="products"
    )

    subcategory = relationship(
        "Subcategory",
        back_populates="products"
    )


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    delivery_address = Column(String, nullable=False)

    total_amount = Column(Numeric(10, 2), nullable=False)

    status = Column(
        String,
        nullable=False,
        default="pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    product_name = Column(
        String,
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    price = Column(
        Numeric(10, 2),
        nullable=False
    )

    subtotal = Column(
        Numeric(10, 2),
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="items"
    )

    product = relationship(
        "Product"
    )