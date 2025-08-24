import json
from pathlib import Path
from typing import Dict, List
from rapidfuzz import process, fuzz
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from .hf_text import get_llm
from .image_caption import image_caption_from_url

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "category_map.json"
CATEGORY_MAP: Dict[str, List[str]] = json.loads(DATA_PATH.read_text())

class Fields(BaseModel):
    name: str = Field(..., description="Product name/title")
    price: float | None = Field(None, description="Numeric price, if mentioned")
    unit: str | None = None
    color: str | None = None
    material: str | None = None
    weight: str | None = None
    dimensions: str | None = None
    stock_qty: int | None = Field(None, description="Item count or quantity")
    tags: List[str] = Field(default_factory=list)
    language: str | None = Field(None, description="ISO-639-1 if identifiable")

def _best_category(text: str) -> str:
    keys: List[str] = []
    for cat, kws in CATEGORY_MAP.items():
        keys.extend([f"{kw}|{cat}" for kw in kws])
    candidates = {k.split("|")[0]: k.split("|")[1] for k in keys}
    match, score, _ = process.extractOne(
        text, candidates.keys(), scorer=fuzz.WRatio
    )
    return candidates[match] if score >= 70 else "Uncategorized"

@tool("auto_categorize", return_direct=False)
def auto_categorize_tool(text: str) -> str:
    """Return best-fit e-commerce category for given text (name/desc)."""
    return _best_category(text)

@tool("image_caption", return_direct=False)
def image_caption_tool(image_url: str) -> str:
    """Caption an image URL to help extraction."""
    return image_caption_from_url(image_url)

@tool("translate", return_direct=False)
def translate_tool(text: str, target_lang: str = "en") -> str:
    """Translate any language to target language using LLM."""
    llm = get_llm(temperature=0.1, max_new_tokens=256)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a careful translator. Preserve product terms/units."),
        ("user", "Translate to {lang}:\n{txt}")
    ])
    chain = prompt | llm
    return chain.invoke({"lang": target_lang, "txt": text}).strip()

@tool("gen_marketing_copy", return_direct=False)
def gen_marketing_copy_tool(structured_json: str, tone: str = "concise") -> str:
    """Generate a market-ready product description from structured fields (JSON string)."""
    llm = get_llm(temperature=0.4, max_new_tokens=300)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an e-commerce copywriter. Write clear, trustworthy copy for small Indian sellers."),
        ("user", "Tone: {tone}\nUse this structured data:\n```json\n{sj}\n```\nWrite an SEO-friendly description (70-120 words).")
    ])
    chain = prompt | llm
    return chain.invoke({"sj": structured_json, "tone": tone}).strip()

def extract_fields(text: str, image_caption: str | None = None) -> Fields:
    llm = get_llm(temperature=0.2, max_new_tokens=256)
    parser = JsonOutputParser(pydantic_object=Fields)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract clean product fields from the user's messy notes. Use numbers when provided. Leave None if unknown."),
        ("user", "User text:\n{txt}\n\nExtra clues (optional): {img_cap}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    chain = prompt | llm | parser
    return chain.invoke({"txt": text, "img_cap": image_caption or ""})
