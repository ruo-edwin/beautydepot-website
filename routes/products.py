from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import get_db
from backend import models, schemas
from routes.auth import get_current_admin


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# ============================================================
# HELPER — VALIDATE PRODUCT
# ============================================================

def validate_product(
    product,
    db: Session,
    exclude_product_id: int | None = None
):
    # --------------------------------------------------------
    # CHECK CATEGORY
    # --------------------------------------------------------

    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == product.category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # --------------------------------------------------------
    # CHECK SUBCATEGORY
    # --------------------------------------------------------

    subcategory = (
        db.query(models.Subcategory)
        .filter(
            models.Subcategory.id == product.subcategory_id
        )
        .first()
    )

    if not subcategory:
        raise HTTPException(
            status_code=404,
            detail="Subcategory not found"
        )

    # --------------------------------------------------------
    # MAKE SURE SUBCATEGORY BELONGS TO CATEGORY
    # --------------------------------------------------------

    if subcategory.category_id != product.category_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Subcategory does not belong to "
                "the selected category"
            )
        )

    # --------------------------------------------------------
    # CHECK BRAND
    # --------------------------------------------------------

    if product.brand_id is not None:

        brand = (
            db.query(models.Brand)
            .filter(
                models.Brand.id == product.brand_id
            )
            .first()
        )

        if not brand:
            raise HTTPException(
                status_code=404,
                detail="Brand not found"
            )

    # --------------------------------------------------------
    # CHECK SLUG
    # --------------------------------------------------------

    slug_query = (
        db.query(models.Product)
        .filter(
            models.Product.slug == product.slug
        )
    )

    if exclude_product_id is not None:
        slug_query = slug_query.filter(
            models.Product.id != exclude_product_id
        )

    existing_slug = slug_query.first()

    if existing_slug:
        raise HTTPException(
            status_code=400,
            detail="Product slug already exists"
        )

    # --------------------------------------------------------
    # CHECK SKU
    # --------------------------------------------------------

    if product.sku:

        sku_query = (
            db.query(models.Product)
            .filter(
                models.Product.sku == product.sku
            )
        )

        if exclude_product_id is not None:
            sku_query = sku_query.filter(
                models.Product.id != exclude_product_id
            )

        existing_sku = sku_query.first()

        if existing_sku:
            raise HTTPException(
                status_code=400,
                detail="SKU already exists"
            )

    # --------------------------------------------------------
    # VALIDATE SALE PRICE
    # --------------------------------------------------------

    if (
        product.sale_price is not None
        and product.sale_price > product.price
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Sale price cannot be higher "
                "than regular price"
            )
        )


# ============================================================
# CREATE PRODUCT
# ADMIN ONLY
# ============================================================

@router.post(
    "/",
    response_model=schemas.ProductResponse
)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):

    validate_product(
        product,
        db
    )

    new_product = models.Product(
        name=product.name,
        slug=product.slug,
        sku=product.sku,
        description=product.description,
        price=product.price,
        sale_price=product.sale_price,
        brand_id=product.brand_id,
        category_id=product.category_id,
        subcategory_id=product.subcategory_id,
        image=product.image,
        is_available=product.is_available,
        is_featured=product.is_featured,
        is_new_arrival=product.is_new_arrival
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# ============================================================
# BULK CREATE PRODUCTS
# ADMIN ONLY
# ============================================================

@router.post(
    "/bulk",
    response_model=list[schemas.ProductResponse]
)
def bulk_create_products(
    data: schemas.ProductBulkCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):

    if not data.products:
        raise HTTPException(
            status_code=400,
            detail="No products were provided"
        )

    # ========================================================
    # VALIDATE ALL PRODUCTS FIRST
    # ========================================================

    slugs_seen = set()
    skus_seen = set()

    for index, product in enumerate(data.products):

        row_number = index + 1

        try:

            validate_product(
                product,
                db
            )

        except HTTPException as exc:

            raise HTTPException(
                status_code=exc.status_code,
                detail=(
                    f"Product row {row_number}: "
                    f"{exc.detail}"
                )
            )

        # ----------------------------------------------------
        # CHECK DUPLICATE SLUGS INSIDE BULK REQUEST
        # ----------------------------------------------------

        if product.slug in slugs_seen:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Product row {row_number}: "
                    "duplicate slug in this upload"
                )
            )

        slugs_seen.add(product.slug)

        # ----------------------------------------------------
        # CHECK DUPLICATE SKUS INSIDE BULK REQUEST
        # ----------------------------------------------------

        if product.sku:

            if product.sku in skus_seen:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Product row {row_number}: "
                        "duplicate SKU in this upload"
                    )
                )

            skus_seen.add(product.sku)

    # ========================================================
    # CREATE PRODUCTS
    # ========================================================

    new_products = []

    for product in data.products:

        new_product = models.Product(
            name=product.name,
            slug=product.slug,
            sku=product.sku,
            description=product.description,
            price=product.price,
            sale_price=product.sale_price,
            brand_id=product.brand_id,
            category_id=product.category_id,
            subcategory_id=product.subcategory_id,
            image=product.image,
            is_available=product.is_available,
            is_featured=product.is_featured,
            is_new_arrival=product.is_new_arrival
        )

        db.add(new_product)
        new_products.append(new_product)

    # ========================================================
    # ONE COMMIT
    # ========================================================

    db.commit()

    for product in new_products:
        db.refresh(product)

    return new_products


# ============================================================
# GET ALL PRODUCTS
# PUBLIC
# ============================================================

@router.get(
    "/",
    response_model=list[schemas.ProductResponse]
)
def get_products(
    db: Session = Depends(get_db)
):

    return (
        db.query(models.Product)
        .filter(
            models.Product.is_available == True
        )
        .order_by(
            models.Product.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET PRODUCTS BY CATEGORY
# PUBLIC
# ============================================================

@router.get(
    "/category/{category_id}",
    response_model=list[schemas.ProductResponse]
)
def get_products_by_category(
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

    return (
        db.query(models.Product)
        .filter(
            models.Product.category_id == category_id
        )
        .order_by(
            models.Product.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET PRODUCTS BY SUBCATEGORY
# PUBLIC
# ============================================================

@router.get(
    "/subcategory/{subcategory_id}",
    response_model=list[schemas.ProductResponse]
)
def get_products_by_subcategory(
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

    return (
        db.query(models.Product)
        .filter(
            models.Product.subcategory_id == subcategory_id
        )
        .order_by(
            models.Product.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET PRODUCTS BY BRAND
# PUBLIC
# ============================================================

@router.get(
    "/brand/{brand_id}",
    response_model=list[schemas.ProductResponse]
)
def get_products_by_brand(
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

    return (
        db.query(models.Product)
        .filter(
            models.Product.brand_id == brand_id
        )
        .order_by(
            models.Product.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET SINGLE PRODUCT
# PUBLIC
# ============================================================

@router.get(
    "/{product_id}",
    response_model=schemas.ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = (
        db.query(models.Product)
        .filter(
            models.Product.id == product_id
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


# ============================================================
# UPDATE PRODUCT
# ADMIN ONLY
# ============================================================

@router.put(
    "/{product_id}",
    response_model=schemas.ProductResponse
)
def update_product(
    product_id: int,
    product_data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):

    # --------------------------------------------------------
    # FIND PRODUCT
    # --------------------------------------------------------

    product = (
        db.query(models.Product)
        .filter(
            models.Product.id == product_id
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # --------------------------------------------------------
    # VALIDATE UPDATED DATA
    # --------------------------------------------------------

    validate_product(
        product_data,
        db,
        exclude_product_id=product_id
    )

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    product.name = product_data.name
    product.slug = product_data.slug
    product.sku = product_data.sku
    product.description = product_data.description
    product.price = product_data.price
    product.sale_price = product_data.sale_price
    product.brand_id = product_data.brand_id
    product.category_id = product_data.category_id
    product.subcategory_id = product_data.subcategory_id
    product.image = product_data.image
    product.is_available = product_data.is_available
    product.is_featured = product_data.is_featured
    product.is_new_arrival = product_data.is_new_arrival

    db.commit()
    db.refresh(product)

    return product


# ============================================================
# DELETE PRODUCT
# ADMIN ONLY
# ============================================================

@router.delete(
    "/{product_id}"
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):

    # --------------------------------------------------------
    # FIND PRODUCT
    # --------------------------------------------------------

    product = (
        db.query(models.Product)
        .filter(
            models.Product.id == product_id
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }