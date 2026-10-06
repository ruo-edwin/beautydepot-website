from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session

from backend.db import get_db
from backend import models

from routes import (
    categories,
    subcategories,
    brands,
    products,
    auth,
    orders,
    upload
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Beauty Ecommerce API",
    version="1.0.0"
)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory="frontend"
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory="frontend/static"),
    name="static"
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(
    categories.router,
    prefix="/api"
)

app.include_router(
    subcategories.router,
    prefix="/api"
)

app.include_router(
    brands.router,
    prefix="/api"
)

app.include_router(
    products.router,
    prefix="/api"
)

app.include_router(
    auth.router,
    prefix="/api"
)

app.include_router(
    orders.router,
    prefix="/api"
)
app.include_router(
    upload.router,
    prefix="/api"
)

# ============================================================
# CUSTOMER HOMEPAGE
# ============================================================

@app.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # ACTIVE CATEGORIES
    # --------------------------------------------------------

    categories_list = (
        db.query(models.Category)
        .filter(
            models.Category.is_active == True
        )
        .order_by(
            models.Category.id
        )
        .all()
    )


    # --------------------------------------------------------
    # FEATURED PRODUCTS
    # --------------------------------------------------------

    featured_products = (
        db.query(models.Product)
        .filter(
            models.Product.is_available == True,
            models.Product.is_featured == True
        )
        .order_by(
            models.Product.id.desc()
        )
        .limit(5)
        .all()
    )


    # --------------------------------------------------------
    # ACTIVE BRANDS
    # --------------------------------------------------------

    brands_list = (
        db.query(models.Brand)
        .filter(
            models.Brand.is_active == True
        )
        .order_by(
            models.Brand.name
        )
        .limit(7)
        .all()
    )


    # --------------------------------------------------------
    # RENDER HOMEPAGE
    # --------------------------------------------------------

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "categories": categories_list,
            "featured_products": featured_products,
            "brands": brands_list
        }
    )


# ============================================================
# CUSTOMER PAGES
# ============================================================

@app.get("/shop")
def shop(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="shop.html",
        context={
            "request": request
        }
    )

@app.get("/product/{product_id}")
def product(
    product_id: int,
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="product_details.html",
        context={
            "request": request,
            "product_id": product_id
        }
    )

@app.get("/cart")
def cart(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={
            "request": request
        }
    )


@app.get("/checkout")
def checkout(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "request": request
        }
    )

@app.get("/order-success")
def order_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="order-success.html",
        context={
            "request": request
        }
    )

# ============================================================
# ADMIN
# ============================================================

@app.get("/admin")
def admin_login():
    return FileResponse(
        "frontend/admin_login.html"
    )


@app.get("/admin/dashboard")
def admin_dashboard():
    return FileResponse(
        "frontend/admin_dashboard.html"
    )


@app.get("/admin/categories")
def admin_categories():
    return FileResponse(
        "frontend/admin_categories.html"
    )


@app.get("/admin/subcategories")
def admin_subcategories():
    return FileResponse(
        "frontend/admin_subcategories.html"
    )


@app.get("/admin/brands")
def admin_brands():
    return FileResponse(
        "frontend/admin_brands.html"
    )


@app.get("/admin/products")
def admin_products():
    return FileResponse(
        "frontend/admin_products.html"
    )

@app.get("/admin/orders")
def admin_orders():
    return FileResponse(
        "frontend/admin_orders.html"
    )

