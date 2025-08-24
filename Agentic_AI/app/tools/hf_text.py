from langchain_huggingface import HuggingFaceEndpoint
from ..config import HF_TOKEN, LLM_REPO_ID

def get_llm(max_new_tokens=512, temperature=0.2):
    if not HF_TOKEN:
        raise RuntimeError("Missing HUGGINGFACEHUB_API_TOKEN")
    return HuggingFaceEndpoint(
        repo_id=LLM_REPO_ID,
        task="text-generation",
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        huggingfacehub_api_token=HF_TOKEN,
        do_sample=True,
        repetition_penalty=1.05,
        return_full_text=False
    )
