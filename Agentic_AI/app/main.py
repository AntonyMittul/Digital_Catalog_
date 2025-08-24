from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import io, csv
from .db import init_db, SessionLocal, Product
from .schemas import ProductIn, ProductItem, UpsertOut
from .agent import run_pipeline, upsert_product

app = FastAPI(title="Digital Catalog Agent (HF + LangChain)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
def on_start():
    init_db()

@app.post("/agent/create_listing", response_model=UpsertOut)
async def create_listing(payload: ProductIn):
    item = run_pipeline(
        text_input=payload.text_input,
        image_url=payload.image_url,
        source_lang=payload.source_lang or "auto",
        target_lang=payload.target_lang or "en"
    )
    pid = upsert_product(payload.seller_id, item)
    return {"id": pid, **item}

@app.get("/products", response_model=List[UpsertOut])
def list_products():
    db = SessionLocal()
    try:
        rows = db.query(Product).order_by(Product.id.desc()).all()
        out = []
        for r in rows:
            out.append({
                "id": r.id, "name": r.name, "category": r.category, "price": r.price,
                "unit": r.unit, "color": r.color, "material": r.material, "weight": r.weight,
                "dimensions": r.dimensions, "stock_qty": r.stock_qty,
                "tags": (r.tags or "").split(",") if r.tags else [],
                "description_en": r.description_en, "description_local": r.description_local,
                "image_url": r.image_url
            })
        return out
    finally:
        db.close()

@app.get("/export/csv")
def export_csv():
    db = SessionLocal()
    try:
        rows = db.query(Product).order_by(Product.id.asc()).all()
        headers = ["id","name","category","price","unit","color","material","weight","dimensions","stock_qty","tags","description_en","description_local","image_url"]
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(headers)
        for r in rows:
            writer.writerow([r.id,r.name,r.category,r.price,r.unit,r.color,r.material,r.weight,r.dimensions,r.stock_qty,r.tags,r.description_en,r.description_local,r.image_url])
        return {"filename":"export.csv","content":buf.getvalue()}
    finally:
        db.close()
