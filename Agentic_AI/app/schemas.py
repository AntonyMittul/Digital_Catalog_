from pydantic import BaseModel, Field
from typing import Optional, List

class ProductIn(BaseModel):
    text_input: str = Field(..., description="Free-form voice transcript or typed text")
    image_url: Optional[str] = None
    source_lang: Optional[str] = "auto"  # e.g., 'ta', 'hi', 'bn', or 'auto'
    target_lang: Optional[str] = "en"    # main marketplace language
    seller_id: Optional[str] = "demo"

class ProductItem(BaseModel):
    name: str
    category: str
    price: Optional[float] = None
    unit: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    weight: Optional[str] = None
    dimensions: Optional[str] = None
    stock_qty: Optional[int] = None
    tags: List[str] = []
    description_en: Optional[str] = None
    description_local: Optional[str] = None
    image_url: Optional[str] = None

class UpsertOut(ProductItem):
    id: int
