"""图片上传接口：日记图片和头像共用。只收 jpg/png，≤5MB。"""
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from deps import get_current_user
from models import User

router = APIRouter(tags=["上传"])

UPLOAD_DIR = "uploads"
MAX_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


@router.post("/upload")
def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """上传一张图片，返回可直接访问的 URL（如 /uploads/xxxx.jpg）。"""
    ext = ALLOWED_TYPES.get(file.content_type or "")
    if ext is None:
        raise HTTPException(status_code=400, detail="只支持 jpg / png / webp 图片")

    content = file.file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="图片不能超过 5MB")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(content)

    return {"url": f"/uploads/{filename}"}
