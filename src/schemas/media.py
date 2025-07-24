from pydantic import BaseModel


class MediaDisplaySchema(BaseModel):
    file_url: str  # URL медиафайла
    media_type: str  # Тип медиа (например, "image", "video")
    is_primary: bool  # Является ли этот медиафайл основным для продукта
