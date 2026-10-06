from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import get_db
from backend import models, schemas
from routes.auth import get_current_admin


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# ============================================================
# CREATE CATEGORY
# ADMIN ONLY
# ============================================================

@router.post(
    "/",
    response_model=schemas.CategoryResponse
)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    existing_category = (
        db.query(models.Category)
        .filter(
            models.Category.name == category.name
        )
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    existing_slug = (
        db.query(models.Category)
        .filter(
            models.Category.slug == category.slug
        )
        .first()
    )

    if existing_slug:
        raise HTTPException(
            status_code=400,
            detail="Category slug already exists"
        )

    new_category = models.Category(
        name=category.name,
        slug=category.slug,
        image=category.image,
        is_active=category.is_active
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# ============================================================
# GET ALL CATEGORIES
# PUBLIC
# ============================================================

@router.get(
    "/",
    response_model=list[schemas.CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db)
):
    return (
        db.query(models.Category)
        .order_by(models.Category.name)
        .all()
    )


# ============================================================
# GET SINGLE CATEGORY
# PUBLIC
# ============================================================

@router.get(
    "/{category_id}",
    response_model=schemas.CategoryResponse
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


# ============================================================
# UPDATE CATEGORY
# ADMIN ONLY
# ============================================================

@router.put(
    "/{category_id}",
    response_model=schemas.CategoryResponse
)
def update_category(
    category_id: int,
    category_data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # --------------------------------------------------------
    # CHECK NAME
    # --------------------------------------------------------

    existing_name = (
        db.query(models.Category)
        .filter(
            models.Category.name == category_data.name,
            models.Category.id != category_id
        )
        .first()
    )

    if existing_name:
        raise HTTPException(
            status_code=400,
            detail="Category name already exists"
        )

    # --------------------------------------------------------
    # CHECK SLUG
    # --------------------------------------------------------

    existing_slug = (
        db.query(models.Category)
        .filter(
            models.Category.slug == category_data.slug,
            models.Category.id != category_id
        )
        .first()
    )

    if existing_slug:
        raise HTTPException(
            status_code=400,
            detail="Category slug already exists"
        )

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    category.name = category_data.name
    category.slug = category_data.slug
    category.image = category_data.image
    category.is_active = category_data.is_active

    db.commit()
    db.refresh(category)

    return category


# ============================================================
# DELETE CATEGORY
# ADMIN ONLY
# ============================================================

@router.delete(
    "/{category_id}"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # --------------------------------------------------------
    # PREVENT DELETING CATEGORY WITH PRODUCTS
    # --------------------------------------------------------

    product_count = (
        db.query(models.Product)
        .filter(
            models.Product.category_id == category_id
        )
        .count()
    )

    if product_count > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot delete category because it has "
                f"{product_count} product(s)."
            )
        )

    # --------------------------------------------------------
    # PREVENT DELETING CATEGORY WITH SUBCATEGORIES
    # --------------------------------------------------------

    subcategory_count = (
        db.query(models.Subcategory)
        .filter(
            models.Subcategory.category_id == category_id
        )
        .count()
    )

    if subcategory_count > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot delete category because it has "
                f"{subcategory_count} subcategor"
                f"{'y' if subcategory_count == 1 else 'ies'}."
            )
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    db.delete(category)
    db.commit()

    return {
        "message": "Category deleted successfully"
    }