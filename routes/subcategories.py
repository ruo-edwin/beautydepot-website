from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import get_db
from backend import models, schemas
from routes.auth import get_current_admin


router = APIRouter(
    prefix="/subcategories",
    tags=["Subcategories"]
)


# ============================================================
# CREATE SUBCATEGORY
# ADMIN ONLY
# ============================================================

@router.post(
    "/",
    response_model=schemas.SubcategoryResponse
)
def create_subcategory(
    subcategory: schemas.SubcategoryCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    # --------------------------------------------------------
    # CHECK CATEGORY EXISTS
    # --------------------------------------------------------

    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == subcategory.category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE NAME
    # --------------------------------------------------------

    existing_subcategory = (
        db.query(models.Subcategory)
        .filter(
            models.Subcategory.name == subcategory.name,
            models.Subcategory.category_id == subcategory.category_id
        )
        .first()
    )

    if existing_subcategory:
        raise HTTPException(
            status_code=400,
            detail="Subcategory already exists in this category"
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE SLUG
    # --------------------------------------------------------

    existing_slug = (
        db.query(models.Subcategory)
        .filter(
            models.Subcategory.slug == subcategory.slug
        )
        .first()
    )

    if existing_slug:
        raise HTTPException(
            status_code=400,
            detail="Subcategory slug already exists"
        )

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    new_subcategory = models.Subcategory(
        name=subcategory.name,
        slug=subcategory.slug,
        category_id=subcategory.category_id,
        image=subcategory.image,
        is_active=subcategory.is_active
    )

    db.add(new_subcategory)
    db.commit()
    db.refresh(new_subcategory)

    return new_subcategory


# ============================================================
# GET ALL SUBCATEGORIES
# PUBLIC
# ============================================================

@router.get(
    "/",
    response_model=list[schemas.SubcategoryResponse]
)
def get_subcategories(
    db: Session = Depends(get_db)
):
    return (
        db.query(models.Subcategory)
        .order_by(models.Subcategory.name)
        .all()
    )


# ============================================================
# GET SUBCATEGORIES BY CATEGORY
# PUBLIC
# ============================================================

@router.get(
    "/category/{category_id}",
    response_model=list[schemas.SubcategoryResponse]
)
def get_subcategories_by_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # CHECK CATEGORY EXISTS
    # --------------------------------------------------------

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

    return (
        db.query(models.Subcategory)
        .filter(
            models.Subcategory.category_id == category_id
        )
        .order_by(models.Subcategory.name)
        .all()
    )


# ============================================================
# GET SINGLE SUBCATEGORY
# PUBLIC
# ============================================================

@router.get(
    "/{subcategory_id}",
    response_model=schemas.SubcategoryResponse
)
def get_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db)
):
    subcategory = (
        db.query(models.Subcategory)
        .filter(
            models.Subcategory.id == subcategory_id
        )
        .first()
    )

    if not subcategory:
        raise HTTPException(
            status_code=404,
            detail="Subcategory not found"
        )

    return subcategory


# ============================================================
# UPDATE SUBCATEGORY
# ADMIN ONLY
# ============================================================

@router.put(
    "/{subcategory_id}",
    response_model=schemas.SubcategoryResponse
)
def update_subcategory(
    subcategory_id: int,
    subcategory_data: schemas.SubcategoryCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    # --------------------------------------------------------
    # FIND SUBCATEGORY
    # --------------------------------------------------------

    subcategory = (
        db.query(models.Subcategory)
        .filter(
            models.Subcategory.id == subcategory_id
        )
        .first()
    )

    if not subcategory:
        raise HTTPException(
            status_code=404,
            detail="Subcategory not found"
        )

    # --------------------------------------------------------
    # CHECK NEW CATEGORY EXISTS
    # --------------------------------------------------------

    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == subcategory_data.category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE NAME
    # --------------------------------------------------------

    existing_name = (
        db.query(models.Subcategory)
        .filter(
            models.Subcategory.name == subcategory_data.name,
            models.Subcategory.category_id == subcategory_data.category_id,
            models.Subcategory.id != subcategory_id
        )
        .first()
    )

    if existing_name:
        raise HTTPException(
            status_code=400,
            detail="Subcategory already exists in this category"
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE SLUG
    # --------------------------------------------------------

    existing_slug = (
        db.query(models.Subcategory)
        .filter(
            models.Subcategory.slug == subcategory_data.slug,
            models.Subcategory.id != subcategory_id
        )
        .first()
    )

    if existing_slug:
        raise HTTPException(
            status_code=400,
            detail="Subcategory slug already exists"
        )

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    subcategory.name = subcategory_data.name
    subcategory.slug = subcategory_data.slug
    subcategory.category_id = subcategory_data.category_id
    subcategory.image = subcategory_data.image
    subcategory.is_active = subcategory_data.is_active

    db.commit()
    db.refresh(subcategory)

    return subcategory


# ============================================================
# DELETE SUBCATEGORY
# ADMIN ONLY
# ============================================================

@router.delete(
    "/{subcategory_id}"
)
def delete_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    # --------------------------------------------------------
    # FIND SUBCATEGORY
    # --------------------------------------------------------

    subcategory = (
        db.query(models.Subcategory)
        .filter(
            models.Subcategory.id == subcategory_id
        )
        .first()
    )

    if not subcategory:
        raise HTTPException(
            status_code=404,
            detail="Subcategory not found"
        )

    # --------------------------------------------------------
    # CHECK FOR PRODUCTS
    # --------------------------------------------------------

    product_count = (
        db.query(models.Product)
        .filter(
            models.Product.subcategory_id == subcategory_id
        )
        .count()
    )

    if product_count > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot delete subcategory because it has "
                f"{product_count} product(s)."
            )
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    db.delete(subcategory)
    db.commit()

    return {
        "message": "Subcategory deleted successfully"
    }