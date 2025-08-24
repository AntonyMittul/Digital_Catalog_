import base64, requests
from ..config import HF_TOKEN, IMG_CAPTION_REPO_ID

def image_caption_from_url(url: str) -> str:
    """
    Uses Hugging Face Inference API to caption an image by URL.
    """
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": url}
    r = requests.post(
        f"https://api-inference.huggingface.co/models/{IMG_CAPTION_REPO_ID}",
        headers=headers, json=payload, timeout=60
    )
    r.raise_for_status()
    data = r.json()
    # BLIP returns [{"generated_text": "..."}]
    if isinstance(data, list) and data and "generated_text" in data[0]:
        return data[0]["generated_text"]
    # some models return dict
    return str(data)
