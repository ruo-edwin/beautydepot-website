from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db import get_db
from backend import models, schemas
from routes.auth import get_current_admin


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# ============================================================
# CREATE ORDER
# ============================================================

@router.post(
    "/",
    response_model=schemas.OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    order_data: schemas.OrderCreate,
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if not order_data.items:
        raise HTTPException(
            status_code=400,
            detail="Your cart is empty."
        )

    for item in order_data.items:
        if item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Product quantity must be at least 1."
            )

    # --------------------------------------------------------
    # CREATE ORDER ITEMS
    # --------------------------------------------------------

    order_items = []
    total_amount = Decimal("0.00")

    for item in order_data.items:

        product = (
            db.query(models.Product)
            .filter(
                models.Product.id == item.product_id
            )
            .first()
        )

        # Product doesn't exist
        if not product:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Product with ID "
                    f"{item.product_id} was not found."
                )
            )

        # Product isn't available
        if not product.is_available:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"{product.name} is currently unavailable."
                )
            )

        # ----------------------------------------------------
        # DETERMINE PRICE
        # ----------------------------------------------------

        if product.sale_price is not None:
            price = Decimal(str(product.sale_price))
        else:
            price = Decimal(str(product.price))

        # ----------------------------------------------------
        # CALCULATE SUBTOTAL
        # ----------------------------------------------------

        subtotal = price * item.quantity

        total_amount += subtotal

        # ----------------------------------------------------
        # CREATE ORDER ITEM
        # ----------------------------------------------------

        order_item = models.OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=item.quantity,
            price=price,
            subtotal=subtotal
        )

        order_items.append(order_item)

    # --------------------------------------------------------
    # CREATE ORDER
    # --------------------------------------------------------

    order = models.Order(
        customer_name=order_data.customer_name.strip(),
        customer_phone=order_data.customer_phone.strip(),
        delivery_address=order_data.delivery_address.strip(),
        total_amount=total_amount,
        status="pending"
    )

    # Attach all items to the order
    order.items = order_items

    # Add order to database
    db.add(order)

    # Save
    db.commit()

    # Refresh so SQLAlchemy gets generated ID,
    # timestamps, etc.
    db.refresh(order)

    return order


# ============================================================
# GET ALL ORDERS
# ADMIN ONLY
# ============================================================

@router.get(
    "/admin",
    response_model=list[schemas.OrderResponse]
)
def get_all_orders(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    orders = (
        db.query(models.Order)
        .order_by(
            models.Order.created_at.desc()
        )
        .all()
    )

    return orders


# ============================================================
# GET SINGLE ORDER — ADMIN
# ADMIN ONLY
# ============================================================

@router.get(
    "/admin/{order_id}",
    response_model=schemas.OrderResponse
)
def get_admin_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    order = (
        db.query(models.Order)
        .filter(
            models.Order.id == order_id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found."
        )

    return order


# ============================================================
# UPDATE ORDER STATUS
# ADMIN ONLY
# ============================================================

@router.patch(
    "/admin/{order_id}/status"
)
def update_order_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    # --------------------------------------------------------
    # ALLOWED STATUSES
    # --------------------------------------------------------

    allowed_statuses = {
        "pending",
        "confirmed",
        "processing",
        "out_for_delivery",
        "completed",
        "cancelled"
    }

    new_status = new_status.strip().lower()

    # --------------------------------------------------------
    # VALIDATE STATUS
    # --------------------------------------------------------

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid order status. "
                "Allowed statuses are: "
                "pending, confirmed, processing, "
                "out_for_delivery, completed, cancelled."
            )
        )

    # --------------------------------------------------------
    # FIND ORDER
    # --------------------------------------------------------

    order = (
        db.query(models.Order)
        .filter(
            models.Order.id == order_id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found."
        )

    # --------------------------------------------------------
    # UPDATE STATUS
    # --------------------------------------------------------

    order.status = new_status

    db.commit()
    db.refresh(order)

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "message": "Order status updated successfully.",
        "order_id": order.id,
        "status": order.status
    }


# ============================================================
# GET SINGLE ORDER
# PUBLIC
# ============================================================

@router.get(
    "/{order_id}",
    response_model=schemas.OrderResponse
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = (
        db.query(models.Order)
        .filter(
            models.Order.id == order_id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found."
        )

    return order