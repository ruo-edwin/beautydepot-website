from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import get_db
from backend import models, schemas
from routes.auth import get_current_admin


router = APIRouter(
    prefix="/brands",
    tags=["Brands"]
)


# ============================================================
# CREATE BRAND
# ADMIN ONLY
# ============================================================

@router.post(
    "/",
    response_model=schemas.BrandResponse
)
def create_brand(
    brand: schemas.BrandCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    # --------------------------------------------------------
    # CHECK DUPLICATE NAME
    # --------------------------------------------------------

    existing_brand = (
        db.query(models.Brand)
        .filter(
            models.Brand.name == brand.name
        )
        .first()
    )

    if existing_brand:
        raise HTTPException(
            status_code=400,
            detail="Brand already exists"
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE SLUG
    # --------------------------------------------------------

    existing_slug = (
        db.query(models.Brand)
        .filter(
            models.Brand.slug == brand.slug
        )
        .first()
    )

    if existing_slug:
        raise HTTPException(
            status_code=400,
            detail="Brand slug already exists"
        )

    # --------------------------------------------------------
    # CREATE BRAND
    # --------------------------------------------------------

    new_brand = models.Brand(
        name=brand.name,
        slug=brand.slug,
        logo=brand.logo,
        is_active=brand.is_active
    )

    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)

    return new_brand


# ============================================================
# GET ALL BRANDS
# PUBLIC
# ============================================================

@router.get(
    "/",
    response_model=list[schemas.BrandResponse]
)
def get_brands(
    db: Session = Depends(get_db)
):
    return (
        db.query(models.Brand)
        .order_by(models.Brand.name)
        .all()
    )


# ============================================================
# GET SINGLE BRAND
# PUBLIC
# ============================================================

@router.get(
    "/{brand_id}",
    response_model=schemas.BrandResponse
)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    brand = (
        db.query(models.Brand)
        .filter(
            models.Brand.id == brand_id
        )
        .first()
    )

    if not brand:
        raise HTTPException(
            status_code=404,
            detail="Brand not found"
        )

    return brand


# ============================================================
# UPDATE BRAND
# ADMIN ONLY
# ============================================================

@router.put(
    "/{brand_id}",
    response_model=schemas.BrandResponse
)
def update_brand(
    brand_id: int,
    brand_data: schemas.BrandCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    # --------------------------------------------------------
    # FIND BRAND
    # --------------------------------------------------------

    brand = (
        db.query(models.Brand)
        .filter(
            models.Brand.id == brand_id
        )
        .first()
    )

    if not brand:
        raise HTTPException(
            status_code=404,
            detail="Brand not found"
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE NAME
    # --------------------------------------------------------

    existing_name = (
        db.query(models.Brand)
        .filter(
            models.Brand.name == brand_data.name,
            models.Brand.id != brand_id
        )
        .first()
    )

    if existing_name:
        raise HTTPException(
            status_code=400,
            detail="Brand name already exists"
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE SLUG
    # --------------------------------------------------------

    existing_slug = (
        db.query(models.Brand)
        .filter(
            models.Brand.slug == brand_data.slug,
            models.Brand.id != brand_id
        )
        .first()
    )

    if existing_slug:
        raise HTTPException(
            status_code=400,
            detail="Brand slug already exists"
        )

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    brand.name = brand_data.name
    brand.slug = brand_data.slug
    brand.logo = brand_data.logo
    brand.is_active = brand_data.is_active

    db.commit()
    db.refresh(brand)

    return brand


# ============================================================
# DELETE BRAND
# ADMIN ONLY
# ============================================================

@router.delete(
    "/{brand_id}"
)
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    # --------------------------------------------------------
    # FIND BRAND
    # --------------------------------------------------------

    brand = (
        db.query(models.Brand)
        .filter(
            models.Brand.id == brand_id
        )
        .first()
    )

    if not brand:
        raise HTTPException(
            status_code=404,
            detail="Brand not found"
        )

    # --------------------------------------------------------
    # CHECK FOR PRODUCTS
    # --------------------------------------------------------

    product_count = (
        db.query(models.Product)
        .filter(
            models.Product.brand_id == brand_id
        )
        .count()
    )

    if product_count > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot delete brand because it has "
                f"{product_count} product(s)."
            )
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    db.delete(brand)
    db.commit()

    return {
        "message": "Brand deleted successfully"
    }