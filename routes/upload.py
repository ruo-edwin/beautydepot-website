import os

import cloudinary
import cloudinary.uploader

from dotenv import load_dotenv
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from routes.auth import get_current_admin


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CLOUDINARY CONFIG
# ============================================================

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"]
)


# ============================================================
# UPLOAD PRODUCT IMAGE
# ============================================================

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    admin=Depends(get_current_admin)
):

    # --------------------------------------------------------
    # CHECK FILE TYPE
    # --------------------------------------------------------

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG and WebP images are allowed."
        )


    # --------------------------------------------------------
    # READ FILE
    # --------------------------------------------------------

    contents = await file.read()


    # --------------------------------------------------------
    # CHECK FILE SIZE
    # --------------------------------------------------------

    max_size = 5 * 1024 * 1024

    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail="Image must be 5MB or smaller."
        )


    # --------------------------------------------------------
    # UPLOAD TO CLOUDINARY
    # --------------------------------------------------------

    try:

        result = cloudinary.uploader.upload(
            contents,
            folder="beauty-depot/products"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Image upload failed: {str(e)}"
        )


    # --------------------------------------------------------
    # RETURN IMAGE URL
    # --------------------------------------------------------

    return {
        "url": result["secure_url"],
        "public_id": result.get("public_id")
    }