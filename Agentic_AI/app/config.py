import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
LLM_REPO_ID = os.getenv("LLM_REPO_ID", "mistralai/Mistral-7B-Instruct-v0.3")
IMG_CAPTION_REPO_ID = os.getenv("IMAGE_CAPTION_REPO_ID", "Salesforce/blip-image-captioning-large")
DB_URL = os.getenv("DB_URL", "sqlite:///./catalog.db")
