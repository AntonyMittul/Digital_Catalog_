from typing import Dict, Any
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate
from .tools.hf_text import get_llm
from .tools.catalog_tools import (
    auto_categorize_tool, image_caption_tool,
    translate_tool, gen_marketing_copy_tool, extract_fields
)
from .db import SessionLocal, Product

TOOLS: list[BaseTool] = [
    auto_categorize_tool,
    image_caption_tool,
    translate_tool,
    gen_marketing_copy_tool
]

def build_agent():
    llm = get_llm()
    template = ChatPromptTemplate.from_messages([
        ("system",
         "You are an AI Catalog Agent that builds complete, high-quality product listings. "
         "Use tools when needed. Always produce a JSON summary at the end."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    agent = create_react_agent(llm, TOOLS, template)
    return AgentExecutor(agent=agent, tools=TOOLS, verbose=False, handle_parsing_errors=True)

def run_pipeline(text_input: str, image_url: str | None, source_lang: str, target_lang: str) -> Dict[str, Any]:
    """
    Deterministic pipeline wrapping agent tools for reliability.
    """
    img_cap = None
    if image_url:
        try:
            img_cap = image_caption_tool.invoke({"image_url": image_url})
        except Exception:
            img_cap = None

    # Extract fields from messy text (+ optional image caption)
    fields = extract_fields(text_input, img_cap)

    # Auto category using name + tags + caption
    cat_hint = (fields.name or "") + " " + " ".join(fields.tags)
    if img_cap:
        cat_hint += " " + img_cap
    category = auto_categorize_tool.invoke({"text": cat_hint})

    # Translate name/desc to English if needed and to local if requested
    name_en = translate_tool.invoke({"text": fields.name, "target_lang": target_lang}) if target_lang != fields.language else fields.name
    # Generate description (EN)
    import json as _json
    fields_json = _json.dumps(fields.model_dump(), ensure_ascii=False)
    desc_en = gen_marketing_copy_tool.invoke({"structured_json": fields_json, "tone": "friendly"})

    # Local description (if non-English requested)
    desc_local = None
    if source_lang and source_lang != "auto" and source_lang != target_lang:
        desc_local = translate_tool.invoke({"text": desc_en, "target_lang": source_lang})

    result = {
        "name": name_en,
        "category": category,
        "price": fields.price,
        "unit": fields.unit,
        "color": fields.color,
        "material": fields.material,
        "weight": fields.weight,
        "dimensions": fields.dimensions,
        "stock_qty": fields.stock_qty,
        "tags": fields.tags,
        "description_en": desc_en,
        "description_local": desc_local,
        "image_url": image_url
    }
    return result

def upsert_product(seller_id: str, item: Dict[str, Any]) -> int:
    db = SessionLocal()
    try:
        # upsert by (seller_id + name)
        obj = db.query(Product).filter(
            Product.seller_id == seller_id, Product.name == item["name"]
        ).first()
        if not obj:
            obj = Product(seller_id=seller_id)
        for k, v in item.items():
            setattr(obj, k, v)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj.id
    finally:
        db.close()
